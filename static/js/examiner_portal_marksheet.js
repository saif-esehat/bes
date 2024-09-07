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

                var str = evt.target.id;
                var parts = str.split('_');
                var lastId = parts[parts.length - 1];
                var attendance_id = document.getElementById('attendance_'+lastId).value
                
        

                var attendance_element = document.getElementById('attendance_'+lastId)

                var marksheet_gsk_status =   document.getElementById('marksheet_gsk_status_'+lastId)

                // Get the values of gsk_oral and gsk_practical marks
                var gsk_oral_marks = document.getElementById('gsk_oral_total_marks').innerText.trim();
                var gsk_practical_marks = document.getElementById('gsk_practical_total_marks').innerText.trim();
                
                if (attendance_element.value == '') {

                    alert("Attendance is Mandatory. Please Select Attendance")

                    return ;
                }

                
                // Check if attendance is marked as 'absent' but mek_oral or mek_practical marks are present
                if (attendance_element.value === 'absent' && (gsk_oral_marks !== 0 || gsk_practical_marks !== 0)) {
                    var confirmation = alert("Candidates marks should be 0 in order to marks them absent");
                    if (!confirmation) {
                        return; // If the user cancels, stop further processing
                    }
                }


                var postData = {
                    id: gsk_marksheet_id, // Assuming you want to pass the ID in the request body
                    attendance_id : attendance_id,
                    marksheet_gsk_status:marksheet_gsk_status
                };
                var result = [];


              
                
    
                $.ajax({
                    type: "POST",
                    url: '/confirm/gsk/marksheet',
                    indexValue: {
                        id: gsk_marksheet_id, // Assuming you want to pass the ID in the request body
                        attendance_element : attendance_element,
                        marksheet_gsk_status:marksheet_gsk_status
                    },
                    data: JSON.stringify(postData),
                    contentType: 'application/json',
                    success: function (response) {

               
                        var marksheet_gsk_status = this.indexValue.marksheet_gsk_status
                        this.indexValue.attendance_element.disabled = true
                        var confirm_button_element = this.indexValue.id
                        document.getElementById(confirm_button_element).remove()
                        marksheet_gsk_status.children[0].innerText = 'Confirmed'
                        
                        // debugger
                        // console.log("POST request successful:", response);
                        // location.reload();

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

                var str = evt.target.id;
                var parts = str.split('_');
                var lastId = parts[parts.length - 1];
                var attendance_id = document.getElementById('attendance_'+lastId).value

                var attendance_element = document.getElementById('attendance_'+lastId)

                var marksheet_mek_status =   document.getElementById('marksheet_mek_status_'+lastId)

                // Get the values of mek_oral and mek_practical marks
                var mek_oral_marks = document.getElementById('mek_oral_total_marks').innerText.trim();
                var mek_practical_marks = document.getElementById('mek_practical_total_marks').innerText.trim();

                if (attendance_element.value == '') {

                    alert("Attendance is Mandatory. Please Select Attendance")

                    return ;
                }

                // Check if attendance is marked as 'absent' but mek_oral or mek_practical marks are present
                if (attendance_element.value === 'absent' && (mek_oral_marks !== '' || mek_practical_marks !== '')) {
                    var confirmation = alert("Candidates marks should be 0 in order to marks them absent");
                    if (!confirmation) {
                        return; // If the user cancels, stop further processing
                    }
                }

                debugger;

                var postData = {
                    id: mek_marksheet_id, // Assuming you want to pass the ID in the request body
                    attendance_id: attendance_id,
                    marksheet_mek_status: marksheet_mek_status
                };
                var result = [];


              
                
    
                $.ajax({
                    type: "POST",
                    url: '/confirm/mek/marksheet',
                    indexValue: {
                        id: mek_marksheet_id, // Assuming you want to pass the ID in the request body
                        attendance_element : attendance_element,
                        marksheet_mek_status:marksheet_mek_status
                    },
                    data: JSON.stringify(postData) ,
                    contentType: 'application/json',                    
                    success: function (response) {

                        var marksheet_gsk_status = this.indexValue.marksheet_mek_status
                        this.indexValue.attendance_element.disabled = true
                        var confirm_button_element = this.indexValue.id
                        document.getElementById(confirm_button_element).remove()
                        marksheet_gsk_status.children[0].innerText = 'Confirmed'
                        // debugger
                        console.log("POST request successful:", response);
                        // location.reload();

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
                
                // debugger

                var gsk_oral_marksheet_id = evt.target.id

                var postData = {
                    id: gsk_oral_marksheet_id // Assuming you want to pass the ID in the request body
                };
                var result = [];


              
                
    
                $.ajax({
                    type: "POST",
                    url: '/confirm/ccmcgsk/marksheet',
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

    publicWidget.registry.ExaminerPortalCCMCOral = publicWidget.Widget.extend(
        {
            selector : ".confirm_ccmc_oral_marksheet_class",
            events:{
                'click':"_onConfirmCCMCOral"
            },
            _onConfirmCCMCOral: function(evt){
                
                // debugger

                var gsk_oral_marksheet_id = evt.target.id

                var postData = {
                    id: gsk_oral_marksheet_id // Assuming you want to pass the ID in the request body
                };
                var result = [];


              
                
    
                $.ajax({
                    type: "POST",
                    url: '/confirm/ccmc_oral/marksheet',
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



});