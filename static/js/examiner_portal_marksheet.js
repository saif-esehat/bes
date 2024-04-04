odoo.define('bes.ExaminerPortalMarksheet', function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');


    publicWidget.registry.ExaminerPortalMarksheet = publicWidget.Widget.extend(
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
                    type: "GET",
                    url: '/confirm/gsk/marksheet',
                    data: postData,
                    dataType: 'json',
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

});