odoo.define('bes.age_calculation', function (require) {
    "use strict";

    var core = require('web.core');
    var field_utils = require('web.field_utils');

    var _t = core._t;

    // Function to calculate age based on date of birth
    function calculateAge(dob) {
        if (!dob) {
            return 0;
        }
        var birthDate = new Date(dob);
        var today = new Date();
        var age = today.getFullYear() - birthDate.getFullYear();
        if (today.getMonth() < birthDate.getMonth() || (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age;
    }

    // Add the age calculation function to the Odoo instance
    core.form_widget_registry.add('age_calculation', field_utils.format.integer);
});