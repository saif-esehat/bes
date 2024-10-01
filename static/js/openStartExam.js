odoo.define('bes.OpenStartExam', function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');


    publicWidget.registry.OpenStartExam = publicWidget.Widget.extend(
        {
            selector: ".start_gp_exam",
            events: {
                'click': "start_gp_exam"
            },

            start_gp_exam: function (e) {
                console.log("inside start gp exam");                
                debugger;
                survey_input_id = document.getElementById("survey_input_id").value;
                examiner_token = document.getElementById('examiner_token').value;
                online_subject = document.getElementById('online_subject').value;
                
                fetch('https://api.ipify.org?format=json')
                    .then(response => response.json())
                    .then(data => {
                        console.log("Your IP address is: " + data.ip);

                        var postData = {
                            survey_input_id: survey_input_id,
                            examiner_token: examiner_token,
                            online_subject: online_subject,
                            ip: data.ip
                        }
                        $.ajax({
                            type: "POST",
                            url: "/my/gpexam/startexam",
                            data: JSON.stringify(postData),
                            contentType: 'application/json',
                            success: function (response) {
                                console.log("POST request successful:", response);                                
                            },
                        })
                    })
                    .catch(error => {
                        console.error('Error fetching IP:', error);
                    });


            }
        }
    );
});