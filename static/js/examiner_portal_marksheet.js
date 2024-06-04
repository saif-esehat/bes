odoo.define('bes.ExaminerPortalMarksheet', function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');


    publicWidget.registry.ExaminerPortalGSKMarksheet = publicWidget.Widget.extend(
        {
            selector : ".confirm_gsk_marksheet_class",
            events:{
                'click':"_onConfirmGSKMarksheet"
            },
            _onConfirmGSKMarksheet: function(evt){
                
                var gsk_marksheet_id = evt.target.id

                var postData = {
                    id: gsk_marksheet_id // Assuming you want to pass the ID in the request body
                };
                var result = [];


              
                
    
                $.ajax({
                    type: "POST",
                    url: '/confirm/gsk/marksheet',
                    data: JSON.stringify(postData),
                    contentType: 'application/json',
                    success: function (response) {

                        // debugger
                        console.log("POST request successful:", response);
                        location.reload();

                        // if response["status"]
                        // Handle success response
                    },
                    error: function (xhr, status, error) {
                        // debugger
                        console.error("POST request failed:", error);
                        
                        // Handle error
                    }
                });

            }
        }
    ),

    publicWidget.registry.ExaminerPortalMEKMarksheet = publicWidget.Widget.extend(
        {
            selector : ".confirm_mek_marksheet_class",
            events:{
                'click':"_onConfirmMEKMarksheet"
            },
            _onConfirmMEKMarksheet: function(evt){
                
                var mek_marksheet_id = evt.target.id

                var postData = {
                    id: mek_marksheet_id // Assuming you want to pass the ID in the request body
                };
                var result = [];


              
                
    
                $.ajax({
                    type: "POST",
                    url: '/confirm/mek/marksheet',
                    data: JSON.stringify(postData) ,
                    contentType: 'application/json',                    
                    success: function (response) {
                        // debugger
                        console.log("POST request successful:", response);
                        location.reload();

                        // if response["status"]
                        // Handle success response
                    },
                    error: function (xhr, status, error) {
                        // debugger
                        console.error("POST request failed:", error);
                        
                        // Handle error
                    }
                });

            }
        }
    )

    publicWidget.registry.ExaminerPortalCCMCGSKOral = publicWidget.Widget.extend(
        {
            selector : ".confirm_ccmc_gsk_oral_marksheet_class",
            events:{
                'click':"_onConfirmCCMCGSKOral"
            },
            _onConfirmCCMCGSKOral: function(evt){
                
                debugger

                var gsk_oral_marksheet_id = evt.target.id

                var postData = {
                    id: mek_marksheet_id // Assuming you want to pass the ID in the request body
                };
                var result = [];


              
                
    
                // $.ajax({
                //     type: "POST",
                //     url: '/confirm/mek/marksheet',
                //     data: JSON.stringify(postData) ,
                //     contentType: 'application/json',                    
                //     success: function (response) {
                //         // debugger
                //         console.log("POST request successful:", response);
                //         location.reload();

                //         // if response["status"]
                //         // Handle success response
                //     },
                //     error: function (xhr, status, error) {
                //         // debugger
                //         console.error("POST request failed:", error);
                        
                //         // Handle error
                //     }
                // });

            }
        }
    )



});