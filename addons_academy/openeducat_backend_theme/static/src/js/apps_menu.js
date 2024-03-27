odoo.define('openeducat_backend_theme.AppsMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var AppsMenu = require('web.AppsMenu');

    var Qweb = core.qweb;

    AppsMenu.include({
        events: _.extend({}, AppsMenu.prototype.events, {
            'input .o_search_box': '_onAppsSearch',
            'click .full': '_onToggleClicked',
        }),
        /**
         * @override
         * @param {web.Widget} parent
         * @param {Object} menuData
         * @param {Object[]} menuData.children
         */
        init: function (parent, menuData) {
            this._super.apply(this, arguments);
            this._activeApp = undefined;
            this._searchApps = [];
            this._apps = _.map(menuData.children, function (appMenuData) {
                return {
                    actionID: parseInt(appMenuData.action.split(',')[1]),
                    menuID: appMenuData.id,
                    name: appMenuData.name,
                    xmlID: appMenuData.xmlid,
                    icon: appMenuData.web_icon_data
                };
            });
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @returns {Object[]}
         */
        getApps: function () {
            return this._apps;
        },
        /**
         * Open the first app in the list of apps
         */
        openFirstApp: function () {
            var firstApp = this._apps[0];
            this._openApp(firstApp);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Object} app
         */
        _openApp: function (app) {
            this._setActiveApp(app);
            this.trigger_up('app_clicked', {
                action_id: app.actionID,
                menu_id: app.menuID,
            });
        },
        /**
         * @private
         * @param {Object} app
         */
        _setActiveApp: function (app) {
            var $oldActiveApp = this.$('.o_app.active');
            $oldActiveApp.removeClass('active');
            var $newActiveApp = this.$('.o_app[data-action-id="' + app.actionID + '"]');
            $newActiveApp.addClass('active');
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        _onAppsSearch: function (ev) {
            ev.preventDefault();
            var search_txt = $(ev.currentTarget).val().trim().toLowerCase();
            if (search_txt.length) {
                this._searchApps = _.filter(this._apps, function (app) {
                    return app.name.toLowerCase().indexOf(search_txt) !== -1;
                });
            } else {
                this._searchApps = this._apps;
            }
            var html = Qweb.render('AppsSearch', {apps: this._searchApps});
            this.$el.find('.o_apps_container').replaceWith(html);
        },

        _onToggleClicked: function (ev) {
            ev.preventDefault();
            this._onOpenCloseDashboard();
        },
        _onOpenCloseDashboard: function (flag) {
            var $navbar = this.$el.parents('.o_main_navbar');
            var $menu_tray = $navbar.find('.o_menu_brand, .o_menu_sections');
            var $toggle_btn = this.$el.find('.full > i');
            var $dashboard = this.$el.find('#apps_menu');
            if (!$dashboard || !$dashboard.length) {
                $dashboard = $navbar.find('#apps_menu');
            }
            if (!$toggle_btn || !$toggle_btn.length) {
                $toggle_btn = $navbar.find('.full > i');
            }

            if (!$dashboard.hasClass('d-none')) {
                $toggle_btn.addClass('fa-th').removeClass('fa-chevron-left');
                $menu_tray.show();
                $dashboard.addClass('d-none');
            } else {
                if (!flag) {
                    $toggle_btn.addClass('fa-chevron-left').removeClass('fa-th');
                    $menu_tray.hide();
                    $dashboard.removeClass('d-none');
                }
            }
        }
    });

    return AppsMenu;

});
