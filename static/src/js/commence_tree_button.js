odoo.define('button_near_create.tree_button', function (require) {
    "use strict";

    console.log("commence_tree_button.js is loaded");

    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var rpc = require('web.rpc'); // Import RPC module

    var TreeButton = ListController.extend({
        buttons_template: 'button_near_create.buttons',
        events: Object.assign({}, ListController.prototype.events, {
            'click .open_wizard_action': '_OpenWizard',
        }),

        _OpenWizard: function () {
            var self = this;
            console.log("Opening Wizard...");

            rpc.query({
                model: 'exam.type.oral.practical.examiners',
                method: 'commence_online_exam',
                args: [[]], // No record selection needed
            }).then(function (action) {
                if (action && action.type === 'ir.actions.act_window') {
                    console.log("Action Received:", action);
                    self.do_action(action); // Open the wizard
                } else {
                    console.error("Invalid action response:", action);
                    self.do_warn("Error", "Invalid response received from server.");
                }
            }).catch(function (error) {
                console.error("Error calling commence_online_exam:", error);
                self.do_warn("Error", "Failed to open wizard. Check server logs.");
            });
        }
    });

    var ExamListView = ListView.extend({
        config: Object.assign({}, ListView.prototype.config, {
            Controller: TreeButton,
        }),
    });

    viewRegistry.add('button_in_tree', ExamListView);
});
