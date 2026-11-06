/* ==========================================================================
   Little Lemon - shared frontend logic
   - API helper (JSON, DRF token, CSRF)
   - Auth state (token stored in localStorage, verified against /api/me/)
   - Cart (localStorage, no checkout/payment)
   - Menu card rendering helpers
   - Mobile navigation toggle
   ========================================================================== */
(function () {
    'use strict';

    var TOKEN_KEY = 'littlelemon_token';
    var USER_KEY = 'littlelemon_username';
    var CART_KEY = 'littlelemon_cart';

    var FALLBACK_IMG = 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=800&q=80';

    var CATEGORY_LABELS = {
        starters: 'Starters',
        main: 'Main Course',
        desserts: 'Desserts',
        drinks: 'Drinks'
    };

    /* ---------------------------------------------------------------- utils */

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : null;
    }

    function escapeHtml(value) {
        return String(value === null || value === undefined ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatPrice(value) {
        var n = Number(value);
        return '$' + (isNaN(n) ? '0.00' : n.toFixed(2));
    }

    /** Turn a DRF error payload into a readable sentence. */
    function formatApiErrors(data, fallback) {
        if (!data) return fallback || 'Something went wrong. Please try again.';
        if (typeof data === 'string') return data;
        if (data.detail) return data.detail;
        var parts = [];
        Object.keys(data).forEach(function (key) {
            var val = data[key];
            var msg = Array.isArray(val) ? val.join(' ') : String(val);
            if (key === 'non_field_errors') {
                parts.push(msg);
            } else {
                var label = key.replace(/_/g, ' ');
                parts.push(label.charAt(0).toUpperCase() + label.slice(1) + ': ' + msg);
            }
        });
        return parts.length ? parts.join(' ') : (fallback || 'Request failed.');
    }

    /* ------------------------------------------------------------ API layer */

    /**
     * fetch() wrapper. Resolves to { ok, status, data }.
     * Network failures resolve with ok=false and status=0 instead of throwing.
     */
    function api(path, options) {
        options = options || {};
        var headers = { 'Accept': 'application/json' };
        if (options.body !== undefined) headers['Content-Type'] = 'application/json';

        var csrf = getCookie('csrftoken');
        if (csrf) headers['X-CSRFToken'] = csrf;

        var token = auth.getToken();
        if (token && options.auth !== false) headers['Authorization'] = 'Token ' + token;

        return fetch(path, {
            method: options.method || 'GET',
            headers: headers,
            credentials: 'same-origin',
            body: options.body !== undefined ? JSON.stringify(options.body) : undefined
        }).then(function (response) {
            if (response.status === 204) {
                return { ok: response.ok, status: response.status, data: null };
            }
            return response.json().catch(function () { return null; }).then(function (data) {
                return { ok: response.ok, status: response.status, data: data };
            });
        }).catch(function () {
            return {
                ok: false,
                status: 0,
                data: { detail: 'Could not reach the server. Make sure Django is running (python manage.py runserver).' }
            };
        });
    }

    /* ----------------------------------------------------------------- auth */

    var auth = {
        getToken: function () { return localStorage.getItem(TOKEN_KEY); },
        getUsername: function () { return localStorage.getItem(USER_KEY); },
        isLoggedIn: function () { return !!localStorage.getItem(TOKEN_KEY); },
        save: function (token, username, isStaff) {
            localStorage.setItem(TOKEN_KEY, token);
            localStorage.setItem(USER_KEY, username);
            if (isStaff !== undefined) {
                localStorage.setItem('littlelemon_is_staff', isStaff ? 'true' : 'false');
            }
        },
        isStaff: function () {
            return localStorage.getItem('littlelemon_is_staff') === 'true';
        },
        clear: function () {
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
            localStorage.removeItem('littlelemon_is_staff');
        },
        /** Ask the server who owns the stored token; clears stale tokens. */
        verify: function () {
            if (!auth.isLoggedIn()) return Promise.resolve(null);
            return api('/api/me/').then(function (res) {
                if (res.ok && res.data) {
                    localStorage.setItem(USER_KEY, res.data.username);
                    if (res.data.is_staff !== undefined) {
                        localStorage.setItem('littlelemon_is_staff', res.data.is_staff ? 'true' : 'false');
                    }
                    return res.data;
                }
                if (res.status === 401 || res.status === 403) auth.clear();
                return null;
            });
        },
        logout: function () {
            return api('/api/logout/', { method: 'POST' }).then(function (res) {
                // Clear locally even if the token was already invalid on the server
                auth.clear();
                return res;
            });
        }
    };

    function renderNavAuth() {
        var slot = document.getElementById('nav-auth');
        if (!slot) return;
        if (auth.isLoggedIn()) {
            slot.innerHTML =
                '<span class="nav-user">Hi, ' + escapeHtml(auth.getUsername()) + '</span>' +
                '<button type="button" class="nav-btn nav-btn-outline" id="nav-logout">Logout</button>';
            document.getElementById('nav-logout').addEventListener('click', function () {
                this.disabled = true;
                auth.logout().then(function () { window.location.href = '/login/?logged_out=1'; });
            });
        } else {
            slot.innerHTML =
                '<a href="/login/" class="nav-btn nav-btn-outline">Login</a>' +
                '<a href="/register/" class="nav-btn">Register</a>';
        }
    }

    /* ----------------------------------------------------------------- cart */

    var cart = {
        read: function () {
            try {
                var items = JSON.parse(localStorage.getItem(CART_KEY) || '[]');
                return Array.isArray(items) ? items : [];
            } catch (e) {
                return [];
            }
        },
        write: function (items) {
            localStorage.setItem(CART_KEY, JSON.stringify(items));
            renderCartBadge();
            document.dispatchEvent(new CustomEvent('cart:changed'));
        },
        add: function (item) {
            var items = cart.read();
            var existing = items.find(function (i) { return i.id === item.id; });
            if (existing) {
                existing.quantity += 1;
            } else {
                items.push({ id: item.id, title: item.title, price: Number(item.price), image_url: item.image_url, quantity: 1 });
            }
            cart.write(items);
        },
        setQuantity: function (id, quantity) {
            var items = cart.read();
            if (quantity <= 0) {
                items = items.filter(function (i) { return i.id !== id; });
            } else {
                items.forEach(function (i) { if (i.id === id) i.quantity = quantity; });
            }
            cart.write(items);
        },
        remove: function (id) { cart.setQuantity(id, 0); },
        clear: function () { cart.write([]); },
        count: function () {
            return cart.read().reduce(function (sum, i) { return sum + i.quantity; }, 0);
        },
        total: function () {
            return cart.read().reduce(function (sum, i) { return sum + i.price * i.quantity; }, 0);
        }
    };

    function renderCartBadge() {
        var badge = document.getElementById('cart-count');
        if (!badge) return;
        var count = cart.count();
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }

    /* ------------------------------------------------------- UI components */

    function showAlert(el, type, message) {
        if (!el) return;
        el.className = 'form-alert form-alert-' + type;
        el.textContent = message;
        el.style.display = 'block';
    }

    function hideAlert(el) {
        if (!el) return;
        el.style.display = 'none';
        el.textContent = '';
    }

    function setLoading(button, loading, loadingText) {
        if (!button) return;
        if (loading) {
            button.dataset.originalText = button.textContent;
            button.textContent = loadingText || 'Please wait...';
            button.disabled = true;
        } else {
            button.textContent = button.dataset.originalText || button.textContent;
            button.disabled = false;
        }
    }

    /** Build a menu card. options.showAdd adds an "Add to Cart" button. */
    function menuCardHtml(item, options) {
        options = options || {};
        var img = item.image_url || FALLBACK_IMG;
        var category = item.category_display || CATEGORY_LABELS[item.category] || '';
        var soldOut = Number(item.inventory) <= 0;
        var footer = options.showAdd
            ? '<button type="button" class="btn-add-cart" data-add-id="' + item.id + '"' + (soldOut ? ' disabled' : '') + '>' +
              (soldOut ? 'Sold out' : '+ Add to Cart') + '</button>'
            : '<a href="/order/" class="delivery-link"><span>Order a delivery</span> &#128757;</a>';

        return '' +
            '<article class="special-card">' +
                '<div class="card-img-wrap">' +
                    '<img src="' + escapeHtml(img) + '" alt="' + escapeHtml(item.title) + '" class="special-card-img" loading="lazy" ' +
                    'onerror="this.onerror=null;this.src=\'' + FALLBACK_IMG + '\'">' +
                    (category ? '<span class="card-category">' + escapeHtml(category) + '</span>' : '') +
                '</div>' +
                '<div class="special-card-content">' +
                    '<div class="special-card-title-row">' +
                        '<h3>' + escapeHtml(item.title) + '</h3>' +
                        '<span class="special-card-price">' + formatPrice(item.price) + '</span>' +
                    '</div>' +
                    '<p class="special-card-desc">' + escapeHtml(item.description || 'Freshly prepared with seasonal Mediterranean ingredients.') + '</p>' +
                    footer +
                '</div>' +
            '</article>';
    }

    function stateHtml(type, message) {
        return '<div class="state-box state-' + type + '">' + escapeHtml(message) + '</div>';
    }

    /* ------------------------------------------------------------ navigation */

    function initNav() {
        var toggle = document.getElementById('nav-toggle');
        var nav = document.getElementById('site-nav');
        if (toggle && nav) {
            toggle.addEventListener('click', function () {
                var open = nav.classList.toggle('open');
                toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        initNav();
        renderNavAuth();
        renderCartBadge();
        // Re-check the token with the server; update nav if it was stale
        auth.verify().then(renderNavAuth);
    });

    window.LittleLemon = {
        api: api,
        auth: auth,
        cart: cart,
        escapeHtml: escapeHtml,
        formatPrice: formatPrice,
        formatApiErrors: formatApiErrors,
        showAlert: showAlert,
        hideAlert: hideAlert,
        setLoading: setLoading,
        menuCardHtml: menuCardHtml,
        stateHtml: stateHtml,
        renderNavAuth: renderNavAuth,
        CATEGORY_LABELS: CATEGORY_LABELS
    };
})();

