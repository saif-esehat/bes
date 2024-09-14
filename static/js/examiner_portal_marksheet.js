odoo.define('bes.ExaminerPortalMarksheet', function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');


    publicWidget.registry.ExaminerPortalGSKOnlineAttendance = publicWidget.Widget.extend(
        {
            selector : ".confirm_online_attendance",
            events:{
                'click':"_onConfirmOnlineAttendance"
            },
            _onConfirmOnlineAttendance: function(evt){


                var marksheet_id = document.getElementById("confirm_modal_marksheet_id").value
                var subject = document.getElementById("confirm_modal_subject").value
                var attendance = document.getElementById("confirm_modal_attendance").value
                debugger
                var postData = {
                    marksheet_id: marksheet_id,
                    subject :subject,
                    attendance:attendance
                };
                $.ajax({
                    type: "POST",
                    url: '/confirm/online/marksheet',
                    indexValue: {
                        marksheet_id: marksheet_id,
                        
                    },
                    data: JSON.stringify(postData),
                    contentType: 'application/json',
                    success: function (response) {
                        debugger
                        var marksheet_id = this.indexValue.marksheet_id;
                        var data = JSON.parse(response.result)
                        if (data.token ) {
                        document.getElementById("online_token_"+marksheet_id.toString()).innerText = data.token
                        document.getElementById("attendance_confirm_"+marksheet_id.toString()).remove();
                        document.getElementById("attendance_dropdown_"+marksheet_id.toString()).disabled=true;

                        }else{
                            document.getElementById("attendance_confirm_"+marksheet_id.toString()).remove();
                            document.getElementById("attendance_dropdown_"+marksheet_id.toString()).disabled=true;
                        }

                        var modal = document.getElementById("attendanceConfirmationModal");
                        if (modal) {
                            $(modal).modal("hide"); // Assuming you are using Bootstrap for the modal
                        }
                        

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
                var gsk_oral_marks = document.getElementById('gsk_oral_total_marks_'+lastId).innerText.trim();
                var gsk_practical_marks = document.getElementById('gsk_practical_total_marks_'+lastId).innerText.trim();
                

                

                if (attendance_element.value == '') {

                    alert("Attendance is Mandatory. Please Select Attendance")

                    return ;
                }
                
                // Check if attendance is marked as 'absent' but mek_oral or mek_practical marks are present
                if (attendance_element.value === 'absent' && (parseInt(gsk_oral_marks) !== 0 || parseInt(gsk_practical_marks) !== 0)) {
                    alert("Candidates marks should be 0 in order to marks them absent");
                    return;
                }

                // Check if attendance is marked as 'present' but oral or practical marks are not present
                if (attendance_element.value === 'present' && (parseInt(gsk_oral_marks) == 0 || parseInt(gsk_practical_marks) == 0)) {
                    var confirmation = confirm("Are you sure you want to mark this candidate present even though their marks are 0?");   
                    if(!confirmation){
                        return;
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
                var mek_oral_marks = document.getElementById('mek_oral_total_marks_'+lastId).innerText.trim();
                var mek_practical_marks = document.getElementById('mek_practical_total_marks_'+lastId).innerText.trim();

                if (attendance_element.value == '') {

                    alert("Attendance is Mandatory. Please Select Attendance")

                    return ;
                }

                // Check if attendance is marked as 'absent' but mek_oral or mek_practical marks are present
                if (attendance_element.value === 'absent' && (parseInt(mek_oral_marks) !== 0 || parseInt(mek_practical_marks) !== 0)) {
                        alert("Candidates marks should be 0 in order to marks them absent");

                        return; // If the user cancels, stop further processin
                }
                
                // Check if attendance is marked as 'present' but oral or practical marks are not present
                if (attendance_element.value === 'present' && (parseInt(mek_oral_marks) == 0 || parseInt(mek_practical_marks) == 0)) {
                    var confirmation = confirm("Are you sure you want to mark this candidate present even though their marks are 0?");   
                    if(!confirmation){
                        return;
                    }
                }


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

                var str = evt.target.id;
                var parts = str.split('_');
                var lastId = parts[parts.length - 1];
                var attendance_id = document.getElementById('attendance_'+lastId).value
                
                var attendance_element = document.getElementById('attendance_'+lastId)

                var marksheet_ccmc_status =   document.getElementById('marksheet_ccmc_gsk_status_'+lastId)

                var ccmc_total_marks = document.getElementById('marksheet_ccmc_gsk_total_'+lastId).innerText.trim();



                if (attendance_element.value == '') {

                    alert("Attendance is Mandatory. Please Select Attendance")

                    return ;
                }

                if (attendance_element.value === 'absent' && (parseInt(ccmc_total_marks) !== 0 )) {
                    alert("Candidates marks should be 0 in order to marks them absent");

                    return; // If the user cancels, stop further processin
                }




                

                var postData = {
                    id: gsk_oral_marksheet_id, // Assuming you want to pass the ID in the request body
                    attendance_id: attendance_id,
                    marksheet_ccmc_status: marksheet_ccmc_status,
                    attendance_element:attendance_element
                };
                var result = [];
                
    
                $.ajax({
                    type: "POST",
                    url: '/confirm/ccmcgsk/marksheet',
                    indexValue: {
                        id: gsk_oral_marksheet_id, // Assuming you want to pass the ID in the request body
                        attendance_id: attendance_id,
                        marksheet_ccmc_status: marksheet_ccmc_status,
                        attendance_element:attendance_element
                    },
                    data: JSON.stringify(postData) ,
                    contentType: 'application/json',                    
                    success: function (response) {
                        // debugger
                        var marksheet_ccmc_status = this.indexValue.marksheet_ccmc_status
                        this.indexValue.attendance_element.disabled = true
                        var confirm_button_element = this.indexValue.id
                        document.getElementById(confirm_button_element).remove()
                        marksheet_ccmc_status.children[0].innerText = 'Confirmed'
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

    publicWidget.registry.ExaminerPortalCCMCOral = publicWidget.Widget.extend(
        {
            selector : ".confirm_ccmc_oral_marksheet_class",
            events:{
                'click':"_onConfirmCCMCOral"
            },
            _onConfirmCCMCOral: function(evt){
                
                

                var ccmc_oral_marksheet_id = evt.target.id

                var str = evt.target.id;
                var parts = str.split('_');
                var lastId = parts[parts.length - 1];
                var attendance_id = document.getElementById('attendance_'+lastId).value
                
                var attendance_element = document.getElementById('attendance_'+lastId)

                var marksheet_ccmc_status =   document.getElementById('marksheet_cccm_status_'+lastId)


                var ccmc_oral_total_marks = document.getElementById('ccmc_oral_total_'+lastId).innerText.trim();
                var ccmc_prac_total_marks = document.getElementById('ccmc_prac_total_'+lastId).innerText.trim();

                debugger


                if (attendance_element.value == '') {

                    alert("Attendance is Mandatory. Please Select Attendance")

                    return ;
                }

                if (attendance_element.value === 'absent' && (parseInt(ccmc_oral_total_marks) !== 0 || parseInt(ccmc_prac_total_marks) !== 0)) {
                    alert("Candidates marks should be 0 in order to marks them absent");

                        return; // If the user cancels, stop further processin
                }

                
                var postData = {
                    id: ccmc_oral_marksheet_id, // Assuming you want to pass the ID in the request body
                    attendance_element: attendance_element,
                    attendance_id:attendance_id,
                    marksheet_ccmc_status :marksheet_ccmc_status
                };


                var result = [];


              
                
    
                $.ajax({
                    type: "POST",
                    url: '/confirm/ccmc_oral/marksheet',
                    indexValue: {
                        id: ccmc_oral_marksheet_id, // Assuming you want to pass the ID in the request body
                        attendance_element: attendance_element,
                        marksheet_ccmc_status :marksheet_ccmc_status
                    },
                    data: JSON.stringify(postData) ,
                    contentType: 'application/json',                    
                    success: function (response) {
                        // debugger

                        var marksheet_ccmc_oral_status = this.indexValue.marksheet_ccmc_status
                        this.indexValue.attendance_element.disabled = true
                        var confirm_button_element = this.indexValue.id
                        document.getElementById(confirm_button_element).remove()
                        marksheet_ccmc_oral_status.children[0].innerText = 'Confirmed'
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