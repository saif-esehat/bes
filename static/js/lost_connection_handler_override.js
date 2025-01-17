odoo.define('bes.lost_connection_handler_override', function (require) {
    "use strict";

    // Import the original error handler module
    var originalErrorHandler = require('web.core.errors.error_handlers');
    
    // Overriding the original lostConnectionHandler function
    originalErrorHandler.lostConnectionHandler = function (env, error, originalError) {
        // Your custom code
        console.log("Inside custom lost connection handler");

        if (!(error instanceof UncaughtPromiseError)) {
            return false;
        }
        if (originalError instanceof ConnectionLostError) {
            if (this.connectionLostNotifRemove) {
                // Notification already displayed
                return true;
            }

            // Custom notification message for connection lost
            this.connectionLostNotifRemove = env.services.notification.add(
                env._t("Connection lost. Trying to reconnect, once reconnected please refresh the page."),
                { sticky: true }
            );

            let delay = 2000;
            browser.setTimeout(function checkConnection() {
                env.services
                    .rpc("/web/webclient/version_info", {})
                    .then(function () {
                        if (this.connectionLostNotifRemove) {
                            this.connectionLostNotifRemove();
                            this.connectionLostNotifRemove = null;
                        }

                        // Custom notification message for connection restored
                        env.services.notification.add(
                            env._t("Connection restored. Please refresh the page to continue."),
                            { type: "info" }
                        );
                    })
                    .catch(() => {
                        // Retry with exponential backoff
                        delay = delay * 1.5 + 500 * Math.random();
                        browser.setTimeout(checkConnection, delay);
                    });
            }, delay);

            return true;
        }
    };
});
