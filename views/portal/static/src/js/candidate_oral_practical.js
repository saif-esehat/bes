odoo.define('bes.CandidatOralPractical', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.CandidatOralPractical = publicWidget.Widget.extend({

        selector: '#gsk_oral_marks_submit',
        events: {
            'click .gskoralmarkssubmit': '_onSubmitGskOral',
            'change #subject_area1':'_onChangeSubmitArea1',
            'change #subject_area2':'_onChangeSubmitArea2'

        },

        _onSubmitGskOral: function (ev) {
            
            console.log("Working")
        },

        _onChangeSubmitArea2:function(ev){
          var msg = "Value must be smaller than 6"
        },
        
        _onChangeSubmitArea1: function(ev){

            var msg = "Value must be smaller than 9"

            // if(ev.target.value > 9){
            //     // appendErrorMessage()
                
            //     this.appendErrorMessage(ev.target.id, msg)
            // }else
            // {
            //     this.clearErrorMessages()
            // }

        },


        
         appendErrorMessage:function(inputId, errorMessage) {
            var inputElement = document.getElementById(inputId);
            var existingErrorMessage = inputElement.nextElementSibling;
      
            // Check if an error message already exists for the input field
            if (!existingErrorMessage || existingErrorMessage.className !== 'error-message') {
              var errorMessageElement = document.createElement('span');
              errorMessageElement.className = 'error-message';
              errorMessageElement.style.color = 'red';
              errorMessageElement.textContent = errorMessage;
              inputElement.parentNode.insertBefore(errorMessageElement, inputElement.nextSibling);
            }
          },
        
        clearErrorMessages : function() {
            var errorMessages = document.querySelectorAll('.error-message');
            errorMessages.forEach(function (errorMessage) {
              errorMessage.parentNode.removeChild(errorMessage);
            });
          }
    
    });

});    