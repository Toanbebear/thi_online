odoo.define('openeducat_backend_theme.Menu', function (require) {
    "use strict";

    var Menu = require('web.Menu');

    return Menu.include({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.$('.o_menu_systray').find('.dropdown-menu').on('click', function (ev) {
                    self._appsMenu._onOpenCloseDashboard(true);
                });
            });
        },
    });
});
