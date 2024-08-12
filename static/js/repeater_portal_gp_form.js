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
        course.textContent = courseName;
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
        debugger;

        var selectedInstitute = document.getElementById("institute_name");
        var selectedIndex = document.getElementById("institute_name").selectedIndex;
        var InstituteSelected = selectedInstitute.options[selectedIndex].text;

        var courseName = document.getElementById("course_name").value;
        var instituteName = document.getElementById("institute_name").value;
        var otherInstituteName = document.getElementById('other_institute_name').value;


        var candidateCertNo =
          document.getElementById("candidate_cert_no").value;
        var courseStartDate =
          document.getElementById("course_start_date").value;
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
          course.textContent = courseName;
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

    _onSubmitGPRepeater: function (evt) {
      evt.preventDefault();

      var tableData = [];

      var gpstcwlisttable = document
        .getElementById("gpstcwlist")
        .querySelectorAll("tr");
    
      var ship_visit_yes =  document.getElementById('ship_visit_yes').checked

      // debugger

      $.ajax({
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
                  course: cells[1].textContent,
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

    _onSubmitCCMCRepeater: function (evt) {
      evt.preventDefault();
      debugger

      var tableData = [];

      var gpstcwlisttable = document
        .getElementById("ccmcstcwlist")
        .querySelectorAll("tr");
    
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
          

        }
          
          
        },
        error: function(xhr, status, error) {
        // Handle errors
        console.error("Error loading data:", status, error);
        }
    })

  
      // Start HERE
      
      // var certificate_criteria = document.getElementById(
      //   "certificate_criteria"
      // ).value;

      // if (certificate_criteria == "passed" && ship_visit_yes) {
      //   document.getElementById("ccmc_repeater_submission_form").submit();
      // } else {
      //   if (certificate_criteria != 'passed') {
      //     for (var i = 0; i < gpstcwlisttable.length; i++) {
      //       var cells = gpstcwlisttable[i].querySelectorAll("td, input");
      //       var rowData = {
      //         course: cells[1].textContent,
      //         institute_id: cells[2].value,
      //         other_institute_name: cells[4].textContent,
      //         candidate_certificate_no: cells[5].textContent,
      //         course_startdate: cells[6].textContent,
      //         course_enddate: cells[7].textContent,
      //       };
      //       tableData.push(rowData);
      //     }
      
      //     const validCombinations = [
      //       ["bst", "stsdsd"],
      //       ["stsdsd", "pst", "efa", "pssr"],
      //     ];
      
      //     document.getElementById("stcw_table_data").value = JSON.stringify(tableData);
      
      //     var stcw_valid = this._checkCourseCombination(tableData, validCombinations);
      //   }else{
      //       var stcw_valid = true;
      //   }
      
      //   var alert_element = document.getElementById("alert_id");
      //   if (alert_element) {
      //     // Remove existing div if present
      //     var existingDiv = alert_element.querySelector("div");
      //     if (existingDiv) {
      //       alert_element.removeChild(existingDiv);
      //     }
      //   }
      
      //   if (!stcw_valid) {
      //     var newDiv = document.createElement("div");
      //     newDiv.textContent =  "STCW is pending. Minimum requirement is BST + STSTD OR PST+ BFF+ PSSR+ MFA + STSTD";
      //     newDiv.className = "alert alert-danger";
      //     newDiv.setAttribute("role", "alert");
      //     alert_element.appendChild(newDiv);
      //   }
      
      //   if (!ship_visit_yes) {
      //     var newDiv = document.createElement("div");
      //     newDiv.textContent = "Ship Visit Must be Yes in Order to apply for Exam";
      //     newDiv.className = "alert alert-danger";
      //     newDiv.setAttribute("role", "alert");
      //     alert_element.appendChild(newDiv);
      //   }
      
      //   if (stcw_valid && ship_visit_yes) {
      //     document.getElementById("ccmc_repeater_submission_form").submit();
      //   }
      // }

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
