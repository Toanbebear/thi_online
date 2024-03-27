odoo.define('openeducat_backend_theme.WebClient', function (require) {
    "use strict";

    var AbstractWebClient = require('web.WebClient');

    AbstractWebClient.include({
        _on_app_clicked_done: function (ev) {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.menu._appsMenu._onOpenCloseDashboard(true);
            });
        }
    });
});