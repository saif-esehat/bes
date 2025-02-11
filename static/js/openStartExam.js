odoo.define('bes.OpenStartExam', function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');


    publicWidget.registry.OpenStartGPExam = publicWidget.Widget.extend(
        {
            selector: ".start_gp_exam",
            events: {
                'click': "start_gp_exam"
            },

            start_gp_exam: function (e) {
                // e.preventDefault();
                // e.stopPropagation(); 

                debugger;
                // if (!examiner_token) {
                //     alert('Examiner token is empty. Please provide a valid token.');
                //     return; // Stop further process
                // }

                console.log("inside start gp exam");                
                var survey_input_id = document.getElementById("survey_input_id").value;
                var examiner_token = document.getElementById('examiner_token_input').value;
                var online_subject = document.getElementById('online_subject').value;

                if (!examiner_token) {
                    alert('Examiner token is empty. Please provide a valid token.');
                    return; // Stop further process
                }

                
                fetch('https://api.ipify.org?format=json')
                    .then(response => response.json())
                    .then(data => {


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
                                // debugger
                                var data = JSON.parse(response.result)
                                if (data.error) {
                                    alert(data.error)
                                }
                                if (data.success) {
                                    window.open(data.success, '_blank');
                        
                                }
                                // response.resul
                                console.log("POST request successful:", response);                                
                            },
                            error: function (xhr, status, error) {

                                // debugger
                                console.error("POST request failed:", error);
                                
                                // Handle error
                            }
                        })
                    })
                    .catch(error => {

                        console.error('Error fetching IP:', error);
                    });


            }
        }
    );

    publicWidget.registry.OpenStartCCMCExam = publicWidget.Widget.extend(
        {
            selector: ".start_ccmc_exam",
            events: {
                'click': "start_ccmc_exam"
            },

            start_ccmc_exam: function (e) {
                // e.preventDefault();
                // e.stopPropagation(); 
                debugger
                var survey_input_id = document.getElementById("survey_input_id").value;
                var examiner_token = document.getElementById('examiner_token_input').value;
                var online_subject = document.getElementById('online_subject').value;

                if (!examiner_token) {
                    alert('Examiner token is empty. Please provide a valid token.');
                    return; // Stop further process
                }


                fetch('https://api.ipify.org?format=json')
                    .then(response => response.json())
                    .then(data => {


                        var postData = {
                            survey_input_id: survey_input_id,
                            examiner_token: examiner_token,
                            online_subject: online_subject,
                            ip: data.ip
                        }
                        debugger
                        $.ajax({
                            type: "POST",
                            url: "/my/ccmcexam/startexam",
                            data: JSON.stringify(postData),
                            contentType: 'application/json',
                            success: function (response) {
                                // debugger
                                var data = JSON.parse(response.result)
                                if (data.error) {
                                    alert(data.error)
                                }
                                if (data.success) {
                                    window.open(data.success, '_blank');
                        
                                }
                                // response.resul
                                console.log("POST request successful:", response);                                
                            },
                            error: function (xhr, status, error) {

                                // debugger
                                console.error("POST request failed:", error);
                                
                                // Handle error
                            }
                        })
                    })
                    .catch(error => {

                        console.error('Error fetching IP:', error);
                    });

               


            }
        }
    );
});