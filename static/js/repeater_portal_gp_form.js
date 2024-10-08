odoo.define("bes.RepeaterPortal", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");

  (publicWidget.registry.AddSTCWGP = publicWidget.Widget.extend({
    selector: ".add_stcw_gp",
    events: {
      click: "_onAddGP",
    },
    _onAddGP: function (evt) {

      debugger
      
      var selectedInstitute = document.getElementById("institute_name");
      var selectedIndex =
        document.getElementById("institute_name").selectedIndex;
      var InstituteSelected = selectedInstitute.options[selectedIndex].text;

      var courseName = document.getElementById("course_name").value;
      var instituteName = document.getElementById("institute_name").value;
      var otherInstituteName = document.getElementById(
        "other_institute_name"
      ).value;
      var candidateCertNo = document.getElementById("candidate_cert_no").value;
      var courseStartDate = document.getElementById("course_start_date").value;
      var courseEndDate = document.getElementById("course_end_date").value;
      var isFormValid = true;
      const courseStartDatec = new Date(document.getElementById('course_start_date').value);
      const courseEndDatec = new Date(document.getElementById('course_end_date').value);
      
      if (courseStartDatec > courseEndDatec) {
        alert('Course end date cannot be before than course start date.');
        return;
      }


      if (
        courseName === "" ||
        instituteName === "" ||
        candidateCertNo === "" ||
        courseStartDate === "" ||
        courseEndDate === ""
      ) {
        isFormValid = false;
        alert("Please fill in all required fields.");
      }

      if (InstituteSelected === "Others" && otherInstituteName === "") {
        isFormValid = false;
        alert("Please specify the other institute name.");
      }

      // Prevent form submission if validation fails
      if (!isFormValid) {
        console.log("Form validation failed");
      } else {
        var tbody = document.getElementById("gpstcwlist");
        const rows = tbody.getElementsByTagName('tr');
        const restrictedCourseNames = ['efa', 'pssr', 'pst', 'fpff'];


        // if (courseStartDatec > courseEndDatec) {
        //   alert('Course start date cannot be later than course end date.');
        //   return;
        // }

        // if (courseStartDatec < courseEndDatec) {
        //   alert('Course end date cannot be later than course start date.');
        //   return;
        // }

        
        for (let i = 0; i < rows.length; i++) {
          // Get the course name from the current row (keeping original case)
          const course_name = rows[i].getElementsByTagName('td')[1].innerText.toLowerCase();
          const certificate_number = rows[i].getElementsByTagName('td')[4].innerText
          // Get the start and end dates from the current row
          const rowDateFrom = new Date(rows[i].getElementsByTagName('td')[5].innerText);
          const rowDateTo = new Date(rows[i].getElementsByTagName('td')[6].innerText);

          if (certificate_number === candidateCertNo) {
            alert('Duplicate Certificate Value')
            return;  // Prevent submission if 'bst' already exists and the new course is in the restricted list
        }

          if (course_name === 'bst' && restrictedCourseNames.includes(courseName.toLowerCase())) {
            alert('Error: You cannot add this course with "bst" as the course name.');
            return;  // Prevent submission if 'bst' already exists and the new course is in the restricted list
        }
      
          // Check if the new course dates overlap with any existing course dates
          if (
              (courseStartDatec >= rowDateFrom && courseStartDatec <= rowDateTo) ||  // New course starts within an existing course
              (courseEndDatec >= rowDateFrom && courseEndDatec <= rowDateTo) ||  // New course ends within an existing course
              (courseStartDatec <= rowDateFrom && courseEndDatec >= rowDateTo)  // New course spans across the entire duration of an existing course
          ) {
              alert('Course Start Date and End Date is Overlapping from the Previous Certificates');
              return;  // Prevent submission if overlapping dates are found
          }
      
          // Check if the current course in the table is one of the restricted courses (EFA, PSSR, PST, FPFF)
          if (restrictedCourseNames.includes(course_name)) {
              // If the new course being added is 'bst', prevent addition since 'bst' cannot coexist with the restricted courses
              if (courseName.toLowerCase() === 'bst') {  // Convert courseName to lowercase for comparison
                  alert('Error: You cannot add "bst" when any of course from EFA, PSSR, PST, FPFF is present.');
                  return;  // Prevent submission if the new course is 'bst' and a restricted course already exists
              }
          }
      
          // Check if the current course in the table is 'bst' and the new course being added is in the restricted list
          if (course_name === 'bst' && restrictedCourseNames.includes(courseName.toLowerCase())) {
              alert('Error: You cannot add this course with "bst" as the course name.');
              return;  // Prevent submission if 'bst' already exists and the new course is in the restricted list
          }
      
          // Check for duplicate course names
          if (course_name === courseName.toLowerCase()) {
              alert('You cannot add Multiple Courses With the Same Name');
              return;  // Prevent submission if a course with the same name already exists
          }
        }


        // Create a new row element
        var newRow = document.createElement("tr");
        var dynamicID = "stcwrow-" + new Date().getTime();

        newRow.id = dynamicID;

        // Delete
        var action = document.createElement("td");
        var deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.textContent = "Delete";
        deleteButton.className = "primary delete_stcw_gp";
        deleteButton.onclick = function (event) {
          event.target.parentElement.parentElement.remove();
        };
        action.appendChild(deleteButton);
        newRow.appendChild(action);

        // courseName
        var course = document.createElement("td");
        course.textContent = courseName.toUpperCase();  // Convert to uppercase for display
        newRow.appendChild(course);

        var institute = document.createElement("td");
        var institute_id_input = document.createElement("input");
        institute_id_input.id = "institute_id";
        institute_id_input.type = "hidden";
        institute_id_input.value = instituteName;
        newRow.appendChild(institute_id_input);
        institute.textContent = InstituteSelected;
        newRow.appendChild(institute);

        var other_institute_name = document.createElement("td");
        other_institute_name.textContent = otherInstituteName;
        newRow.appendChild(other_institute_name);

        var candidate_certificate = document.createElement("td");
        candidate_certificate.textContent = candidateCertNo;
        newRow.appendChild(candidate_certificate);

        var course_start = document.createElement("td");
        course_start.textContent = courseStartDate;
        newRow.appendChild(course_start);

        var course_end = document.createElement("td");
        course_end.textContent = courseEndDate;
        newRow.appendChild(course_end);

        // Append the new row to the tbody
        tbody.appendChild(newRow);

        // document.getElementById('course_name').value = ''
        // document.getElementById('institute_name').value = ''
        document.getElementById("other_institute_name").value = "";
        document.getElementById("candidate_cert_no").value = "";
        document.getElementById("course_start_date").value = "";
        document.getElementById("course_end_date").value = "";

        var modal = document.getElementById("AddGPRepeaterStcw");
        if (modal) {
          $(modal).modal("hide"); // Assuming you are using Bootstrap for the modal
        }
      }

      // console.log('Course Name:', courseName);
      // console.log('Institute Name:', instituteName);
      // console.log('Other Institute Name:', otherInstituteName);
      // console.log('Candidate Certificate Number:', candidateCertNo);
      // console.log('Course Start Date:', courseStartDate);
      // console.log('Course End Date:', courseEndDate);
    },
  })),
    (publicWidget.registry.AddSTCWCCMC = publicWidget.Widget.extend({
      selector: ".add_stcw_ccmc",
      events: {
        click: "_onAddCCMC",
      },

      
      _onAddCCMC: function (evt) {
        evt.preventDefault();

        var selectedInstitute = document.getElementById("institute_name");
        var selectedIndex = document.getElementById("institute_name").selectedIndex;
        var InstituteSelected = selectedInstitute.options[selectedIndex].text;

        var courseName = document.getElementById("course_name").value;
        var instituteName = document.getElementById("institute_name").value;
        var otherInstituteName = document.getElementById('other_institute_name').value;
        
        const courseStartDatec = new Date(document.getElementById('course_start_date').value);
        const courseEndDatec = new Date(document.getElementById('course_end_date').value);

        //  if (courseStartDatec > courseEndDatec) {
        //       alert('Course start date cannot be later than course end date.');
        //       return;
        //     }

        if (courseStartDatec > courseEndDatec) {
              alert('Course end date cannot be before than course start date.');
              return;
            }

        var candidateCertNo = document.getElementById("candidate_cert_no").value;
        var courseStartDate = document.getElementById("course_start_date").value;
        var courseEndDate = document.getElementById("course_end_date").value;
        var isFormValid = true;

        if (
          courseName === "" ||
          instituteName === "" ||
          candidateCertNo === "" ||
          courseStartDate === "" ||
          courseEndDate === ""
        ) {
          isFormValid = false;
          alert("Please fill in all required fields.");
        }

        if (InstituteSelected === "Others" && otherInstituteName === "") {
          isFormValid = false;
          alert("Please specify the other institute name.");
        }

        // Prevent form submission if validation fails
        if (!isFormValid) {
          console.log("Form validation failed");
        } else {
          var tbody = document.getElementById("ccmcstcwlist");
          const rows = tbody.getElementsByTagName('tr');
          const restrictedCourseNames = ['efa', 'pssr', 'pst', 'fpff'];

          for (let i = 0; i < rows.length; i++) {
            // Get the course name from the current row (keeping original case)
            const course_name = rows[i].getElementsByTagName('td')[1].innerText.toLowerCase();
            const certificate_number = rows[i].getElementsByTagName('td')[4].innerText

            if (certificate_number === candidateCertNo) {
              alert('Duplicate Certificate Value')
              return;  // Prevent submission if 'bst' already exists and the new course is in the restricted list
          }
            // Get the start and end dates from the current row
            const rowDateFrom = new Date(rows[i].getElementsByTagName('td')[5].innerText);
            const rowDateTo = new Date(rows[i].getElementsByTagName('td')[6].innerText);
        
            // Check if the new course dates overlap with any existing course dates
            if (
                (courseStartDatec >= rowDateFrom && courseStartDatec <= rowDateTo) ||  // New course starts within an existing course
                (courseEndDatec >= rowDateFrom && courseEndDatec <= rowDateTo) ||  // New course ends within an existing course
                (courseStartDatec <= rowDateFrom && courseEndDatec >= rowDateTo)  // New course spans across the entire duration of an existing course
            ) {
                alert('Course Start Date and End Date is Overlapping from the Previous Certificates');
                return;  // Prevent submission if overlapping dates are found
            }
        
            // Check if the current course in the table is one of the restricted courses (EFA, PSSR, PST, FPFF)
            if (restrictedCourseNames.includes(course_name)) {
                // If the new course being added is 'bst', prevent addition since 'bst' cannot coexist with the restricted courses
                if (courseName.toLowerCase() === 'bst') {  // Convert courseName to lowercase for comparison
                    alert('Error: You cannot add "bst" when any of course from EFA, PSSR, PST, FPFF is present.');
                    return;  // Prevent submission if the new course is 'bst' and a restricted course already exists
                }
            }
        
            // Check if the current course in the table is 'bst' and the new course being added is in the restricted list
            if (course_name === 'bst' && restrictedCourseNames.includes(courseName.toLowerCase())) {
                alert('Error: You cannot add this course with "bst" as the course name.');
                return;  // Prevent submission if 'bst' already exists and the new course is in the restricted list
            }
        
            // Check for duplicate course names
            if (course_name === courseName.toLowerCase()) {
                alert('You cannot add Multiple Courses With the Same Name');
                return;  // Prevent submission if a course with the same name already exists
            }
          }
        


          


          // Create a new row element
          var newRow = document.createElement("tr");
          var dynamicID = "stcwrow-" + new Date().getTime();

          newRow.id = dynamicID;

          // Delete
          var action = document.createElement("td");
          var deleteButton = document.createElement("button");
          deleteButton.type = "button";
          deleteButton.textContent = "Delete";
          deleteButton.className = "primary delete_stcw_gp";
          deleteButton.onclick = function (event) {
            event.target.parentElement.parentElement.remove();
          };
          action.appendChild(deleteButton);
          newRow.appendChild(action);

          // courseName
          var course = document.createElement("td");
          course.textContent = courseName.toUpperCase();
          newRow.appendChild(course);

          var institute = document.createElement("td");
          var institute_id_input = document.createElement("input");
          institute_id_input.id = "institute_id";
          institute_id_input.type = "hidden";
          institute_id_input.value = instituteName;
          newRow.appendChild(institute_id_input);
          institute.textContent = InstituteSelected;
          newRow.appendChild(institute);

          var other_institute_name = document.createElement("td");
          other_institute_name.textContent = otherInstituteName;
          newRow.appendChild(other_institute_name);

          var candidate_certificate = document.createElement("td");
          candidate_certificate.textContent = candidateCertNo;
          newRow.appendChild(candidate_certificate);

          var course_start = document.createElement("td");
          course_start.textContent = courseStartDate;
          newRow.appendChild(course_start);

          var course_end = document.createElement("td");
          course_end.textContent = courseEndDate;
          newRow.appendChild(course_end);

          // Append the new row to the tbody
          tbody.appendChild(newRow);

          // document.getElementById('course_name').value = ''
          // document.getElementById('institute_name').value = ''
          document.getElementById("other_institute_name").value = "";
          document.getElementById("candidate_cert_no").value = "";
          document.getElementById("course_start_date").value = "";
          document.getElementById("course_end_date").value = "";

          var modal = document.getElementById("AddCCMCRepeaterStcw");
          if (modal) {
            $(modal).modal("hide"); // Assuming you are using Bootstrap for the modal
          }
        }
      },
    })),
    
    (publicWidget.registry.DeleteSTCW = publicWidget.Widget.extend({
      selector: ".delete_stcw_gp",
      events: {
        click: "_onDeleteGP",
      },

      _onDeleteGP: function (evt) {
        console.log("inside delete GP");
        document.getRootNode.remove();
      },
    }));

  publicWidget.registry.submitGPRepeaterForm = publicWidget.Widget.extend({
    selector: 'form[name="gp_repeater_submit"]',
    events: {
      submit: "_onSubmitGPRepeater",
    },

    _onSubmitGPRepeater: async function (evt) {
      evt.preventDefault();

      var tableData = [];

      var gpstcwlisttable = document
        .getElementById("gpstcwlist")
        .querySelectorAll("tr");

      
      var upi_utr_no = document.getElementById("upi_utr_no").value
    
      var ship_visit_yes =  document.getElementById('ship_visit_yes').checked

      var transaction = {
        "upi_utr_no": upi_utr_no,
      }

      let response = await $.ajax({
        url: "/my/checktransaction", // Update the URL with your actual route
        data: JSON.stringify(transaction),
        type: "POST",
        contentType: 'application/json'
    });

      var invoice_valid = JSON.parse(response.result).invoice_valid;
      if (invoice_valid) {
        var alert_element = document.getElementById("alert_id");
        var newDiv = document.createElement("div");
        newDiv.textContent = "UTR number is duplicated , already registered in the system";
        newDiv.className = "alert alert-danger";
        newDiv.setAttribute("role", "alert");
        alert_element.appendChild(newDiv);
        return; // Stop further execution if invoice_valid is true
    }





      // await $.ajax({
      //   url: "/my/checktransaction", // Update the URL with your actual route
      //   data: JSON.stringify(transaction),
      //   type: "POST",
      //   contentType: 'application/json',
      //   success: function (data) {
      //     var alert_element = document.getElementById("alert_id");
      //     var invocie_valid = JSON.parse(data.result).invoice_valid

      //     if (invocie_valid) {

      //       var newDiv = document.createElement("div");
      //       newDiv.textContent = "UPI Transaction already found in the System";
      //       newDiv.className = "alert alert-danger";
      //       newDiv.setAttribute("role", "alert");
      //       alert_element.appendChild(newDiv);
      //       evt.preventDefault();
      //       return;

      //     }


      //   }

      // })
      // debugger

      await $.ajax({
        url: "/my/checkotherinstitutegp", // Update the URL with your actual route
        method: "GET",
        indexValue: {checkCourse:this._checkCourseCombination,},
        dataType: "json",
        success: function(data) {
        // Handle the successful response

        if (!data.other_institute_name) {

          
          
          var alert_element = document.getElementById("alert_id");

          if (!data.other_institute_name) {
              var newDiv = document.createElement("div");
              newDiv.textContent = "Other Institute Name Must be entered";
              newDiv.className = "alert alert-danger";
              newDiv.setAttribute("role", "alert");
              alert_element.appendChild(newDiv);
        }

          
        }else{
          
          var certificate_criteria = document.getElementById(
            "certificate_criteria"
          ).value;
    
          if (certificate_criteria == "passed" && ship_visit_yes) {
            document.getElementById("gp_repeater_submission_form").submit();
          } else {
            if (certificate_criteria != 'passed') {
              for (var i = 0; i < gpstcwlisttable.length; i++) {
                var cells = gpstcwlisttable[i].querySelectorAll("td, input");
                var rowData = {
                  course: cells[1].textContent.toLowerCase(),
                  institute_id: cells[2].value,
                  other_institute_name: cells[4].textContent,
                  candidate_certificate_no: cells[5].textContent,
                  course_startdate: cells[6].textContent,
                  course_enddate: cells[7].textContent,
                };
                tableData.push(rowData);
              }
          
              const validCombinations = [
                ["bst", "stsdsd"],
                ["stsdsd", "pst", "efa", "pssr"],
              ];
          
              document.getElementById("stcw_table_data").value = JSON.stringify(tableData);
          
              var stcw_valid = this.indexValue.checkCourse(tableData, validCombinations);
            }else{
                var stcw_valid = true;
            }
          
            var alert_element = document.getElementById("alert_id");
            if (alert_element) {
              // Remove existing div if present
              var existingDiv = alert_element.querySelector("div");
              if (existingDiv) {
                alert_element.removeChild(existingDiv);
              }
            }
          
            if (!stcw_valid) {
              var newDiv = document.createElement("div");
              newDiv.textContent = "STCW is pending. Minimum requirement is BST + STSTD OR PST+ BFF+ PSSR+ MFA + STSTD";
              newDiv.className = "alert alert-danger";
              newDiv.setAttribute("role", "alert");
              alert_element.appendChild(newDiv);
            }
          
            if (!ship_visit_yes) {
              var newDiv = document.createElement("div");
              newDiv.textContent = "Ship Visit Must be Yes in Order to apply for Exam";
              newDiv.className = "alert alert-danger";
              newDiv.setAttribute("role", "alert");
              alert_element.appendChild(newDiv);
            }
          
            if (stcw_valid && ship_visit_yes) {
              document.getElementById("gp_repeater_submission_form").submit();
            }
          }


        }
          
          
        },
        error: function(xhr, status, error) {
        // Handle errors
        console.error("Error loading data:", status, error);
        }
    });
     
    },

    _checkCourseCombination: function (coursesList, validCombinations) {
      const courseNames = coursesList.map((course) => course.course);

      for (let combination of validCombinations) {
        if (combination.every((course) => courseNames.includes(course))) {
          return true;
        }
      }

      return false;
    }

    // END HERE
  });

  publicWidget.registry.submitCCMCRepeaterForm = publicWidget.Widget.extend({
    selector: 'form[name="ccmc_repeater_submit"]',
    events: {
      submit: "_onSubmitCCMCRepeater",
    },

    _onSubmitCCMCRepeater: async function (evt) {
      evt.preventDefault();
      debugger

      var tableData = [];

      var gpstcwlisttable = document
        .getElementById("ccmcstcwlist")
        .querySelectorAll("tr");
      
      var upi_utr_no = document.getElementById("upi_utr_no").value

      var transaction = {
        "upi_utr_no": upi_utr_no,
      }

      

      let response = await $.ajax({
        url: "/my/checktransaction", // Update the URL with your actual route
        data: JSON.stringify(transaction),
        type: "POST",
        contentType: 'application/json'
    });

      var invoice_valid = JSON.parse(response.result).invoice_valid;
      
      if (invoice_valid) {
        var alert_element = document.getElementById("alert_id");
        var newDiv = document.createElement("div");
        newDiv.textContent = "UTR number is duplicated , already registered in the system";
        newDiv.className = "alert alert-danger";
        newDiv.setAttribute("role", "alert");
        alert_element.appendChild(newDiv);
        return; // Stop further execution if invoice_valid is true
    }
    
      var ship_visit_yes =  document.getElementById('ship_visit_yes').checked

      $.ajax({
        url: "/my/checkotherinstituteccmc", // Update the URL with your actual route
        method: "GET",
        indexValue: {checkCourse:this._checkCourseCombination,},
        dataType: "json",
        success: function(data) {
        // Handle the successful response

        if (!data.other_institute_name) {

          var alert_element = document.getElementById("alert_id");

          if (!data.other_institute_name) {
              var newDiv = document.createElement("div");
              newDiv.textContent = "Other Institute Name Must be entered";
              newDiv.className = "alert alert-danger";
              newDiv.setAttribute("role", "alert");
              alert_element.appendChild(newDiv);
        }

          
        }else{

          var certificate_criteria = document.getElementById(
            "certificate_criteria"
          ).value;
    
          if (certificate_criteria == "passed" && ship_visit_yes) {
            document.getElementById("ccmc_repeater_submission_form").submit();
          } else {
            if (certificate_criteria != 'passed') {
              for (var i = 0; i < gpstcwlisttable.length; i++) {
                var cells = gpstcwlisttable[i].querySelectorAll("td, input");
                var rowData = {
                  course: cells[1].textContent.toLowerCase(),
                  institute_id: cells[2].value,
                  other_institute_name: cells[4].textContent,
                  candidate_certificate_no: cells[5].textContent,
                  course_startdate: cells[6].textContent,
                  course_enddate: cells[7].textContent,
                };
                tableData.push(rowData);
              }
          
              const validCombinations = [
                ["bst", "stsdsd"],
                ["stsdsd", "pst", "efa", "pssr"],
              ];
          
              document.getElementById("stcw_table_data").value = JSON.stringify(tableData);
          
              var stcw_valid = this.indexValue.checkCourse(tableData, validCombinations);
            }else{
                var stcw_valid = true;
            }
          
            var alert_element = document.getElementById("alert_id");
            if (alert_element) {
              // Remove existing div if present
              var existingDiv = alert_element.querySelector("div");
              if (existingDiv) {
                alert_element.removeChild(existingDiv);
              }
            }
          
            if (!stcw_valid) {
              var newDiv = document.createElement("div");
              newDiv.textContent =  "STCW is pending. Minimum requirement is BST + STSTD OR PST+ BFF+ PSSR+ MFA + STSTD";
              newDiv.className = "alert alert-danger";
              newDiv.setAttribute("role", "alert");
              alert_element.appendChild(newDiv);
            }
          
            if (!ship_visit_yes) {
              var newDiv = document.createElement("div");
              newDiv.textContent = "Ship Visit Must be Yes in Order to apply for Exam";
              newDiv.className = "alert alert-danger";
              newDiv.setAttribute("role", "alert");
              alert_element.appendChild(newDiv);
            }
          
            if (stcw_valid && ship_visit_yes) {
              document.getElementById("ccmc_repeater_submission_form").submit();
            }
          }
          

        }
          
          
        },
        error: function(xhr, status, error) {
        // Handle errors
        console.error("Error loading data:", status, error);
        }
    })

  
      // Start HERE
      
     

      // END HERE
      //    debugger
    },

    _checkCourseCombination: function (coursesList, validCombinations) {
      const courseNames = coursesList.map((course) => course.course);

      for (let combination of validCombinations) {
        if (combination.every((course) => courseNames.includes(course))) {
          return true;
        }
      }

      return false;
    },
  });



});
