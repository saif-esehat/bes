odoo.define('bes.RepeaterPortal', function (require) {
    "use strict";


    var publicWidget = require("web.public.widget");
    var ajax = require('web.ajax');

    publicWidget.registry.AddSTCW = publicWidget.Widget.extend(
        {
            selector : ".add_stcw_gp",
            events:{
                'click':"_onAddGP"
            },
            _onAddGP: function(evt){

                var selectedInstitute = document.getElementById('institute_name');
                var selectedIndex = document.getElementById('institute_name').selectedIndex
                var InstituteSelected = selectedInstitute.options[selectedIndex].text;
                
                var courseName = document.getElementById('course_name').value;
                var instituteName = document.getElementById('institute_name').value;
                var otherInstituteName = document.getElementById('other_institute_name').value;
                var candidateCertNo = document.getElementById('candidate_cert_no').value;
                var courseStartDate = document.getElementById('course_start_date').value;
                var courseEndDate = document.getElementById('course_end_date').value;
                var isFormValid = true;

                if (courseName === "" || instituteName === "" || candidateCertNo === "" || courseStartDate === "" || courseEndDate === "") {
                    isFormValid = false;
                    alert("Please fill in all required fields.");
                }
                debugger

                if (InstituteSelected === "Others" && otherInstituteName === "") {
                    isFormValid = false;
                    alert("Please specify the other institute name.");
                }
            
                // Prevent form submission if validation fails
                if (!isFormValid) {
                    console.log("Form validation failed");
               
                }else{

                    var tbody = document.getElementById('gpstcwlist');

                // Create a new row element
                var newRow = document.createElement('tr');
                var dynamicID = 'stcwrow-' + new Date().getTime();
     
                newRow.id = dynamicID;
    


                // Delete
                var action = document.createElement('td');
                var deleteButton = document.createElement('button');
                deleteButton.type = 'button'
                deleteButton.textContent = 'Delete';    
                deleteButton.className = "primary delete_stcw_gp"
                deleteButton.onclick = function(event) {
                    event.target.parentElement.parentElement.remove()
                };
                action.appendChild(deleteButton);
                newRow.appendChild(action);
                
                // courseName
                var course = document.createElement('td');
                course.textContent = courseName
                newRow.appendChild(course);
                
                var institute = document.createElement('td');
                var institute_id_input = document.createElement('input');
                institute_id_input.id = 'institute_id'
                institute_id_input.type = 'hidden';
                institute_id_input.value = instituteName
                newRow.appendChild(institute_id_input);
                institute.textContent = InstituteSelected;
                newRow.appendChild(institute);

                 var other_institute_name = document.createElement('td');
                 other_institute_name.textContent = otherInstituteName
                 newRow.appendChild(other_institute_name);

                 var candidate_certificate = document.createElement('td');
                 candidate_certificate.textContent = candidateCertNo
                 newRow.appendChild(candidate_certificate);

                 var course_start = document.createElement('td');
                 course_start.textContent = courseStartDate;
                 newRow.appendChild(course_start);

                 var course_end = document.createElement('td');
                 course_end.textContent = courseEndDate;
                 newRow.appendChild(course_end);
                
                // Append the new row to the tbody
                tbody.appendChild(newRow);

                // document.getElementById('course_name').value = ''
                // document.getElementById('institute_name').value = ''
                document.getElementById('other_institute_name').value = ''
                document.getElementById('candidate_cert_no').value = ''
                document.getElementById('course_start_date').value = ''
                document.getElementById('course_end_date').value  = ''
                
                

                var modal = document.getElementById('AddGPRepeaterStcw');
                if (modal) {
                    $(modal).modal('hide'); // Assuming you are using Bootstrap for the modal
                }

                }
            
  
                // console.log('Course Name:', courseName);
                // console.log('Institute Name:', instituteName);
                // console.log('Other Institute Name:', otherInstituteName);
                // console.log('Candidate Certificate Number:', candidateCertNo);
                // console.log('Course Start Date:', courseStartDate);
                // console.log('Course End Date:', courseEndDate);

                

            }
}),
        
    
    publicWidget.registry.DeleteStcw = publicWidget.Widget.extend(
                {

                    selector : ".delete_stcw_gp",
                    events:{
                        'click':"_onDeleteGP"
                    },

                    _onDeleteGP : function(evt) {
                       console.log("inside delete GP");
                       document.getRootNode.remove()
                    }
                    
                }
                )
}
);