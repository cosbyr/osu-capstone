$(document).ready(function(){

	$body = $("body");
	
	//$(document).on({
	    //ajaxStart: function() { $body.addClass("loading");    },
	    //ajaxComplete: function() { $body.removeClass("loading"); }    
	//});
	
	/* for find employee form on create a new award */
	$('#get-employee-form').on('submit', function(e){
	 event.preventDefault();

	  var that = $(this),
	      url = that.attr('action'),
	      type = that.attr('method'),
	      data = $("#last-name").val();
	      data = '{"lname":"' + data + '"}';
	      console.log(data);

	  	$.ajax('/get-employee', {
		  	type: 'post',
		  	data: data,
			contentType: 'application/json',
		  	dataType: 'json',

	  		success: function(response) {
	  			//$("input[type=radio][name=employee-to-get-award]").remove()
				$("input[type=radio][name=employee-to-get-award],label[for=employee-to-get-award]").remove()
				
				for (var i in response){
					if(i != 'status' && i != 'message'){
						var details = response[i].fname + " " + response[i].lname + " " +response[i].email;
						//console.log(response[i].fname + " " + response[i].lname + " " +response[i].email);
						$("#choose-employee").append('<label for="employee-to-get-award">' + details +'</label>' );
						$("#choose-employee").append('<input type="radio" name="employee-to-get-award" value="'+ i +'">');
					}
				}
				
		    },

		    error: function (jqXHR, exception) {
		    	console.log("in error state");
		    	console.log(jqXHR.responseText);
    			console.log(jqXHR);
			}
	  	});
	  return false;
	});



	/*if choosing to reset password via email a warning box will apear  in /password*/
	$("#reset-via-email").on("click", function(){
		$("#send-email-reset").removeClass("is-hidden");
		$("#display-security-questions").addClass("is-hidden");
		console.log("button pressed");
	});


	/* choosing to reset via email or password on /password*/
	var email = $("#reset-password").on('submit', function(){
		event.preventDefault();
		var that = $(this),
	      url = that.attr('action'),
	      type = that.attr('method'),
	      radioValue = $("input[name='reset-method']:checked").val();
	      email = $("input[name='email']").val();
		  data = JSON.stringify({'email':email, 'reset-method':radioValue})
	      console.log(data);
		

		$.ajax(url,{
			type: type,
			data: data,
			contentType: 'application/json',
		  	dataType: 'json',
			
			success: function(response){

				$body.removeClass("loading");
				if(radioValue == "email"){
					
					//console.log("I will now display email stuff");
					$("#display-security-questions").addClass("no-display");
					$("#send-email-reset").removeClass("no-display");
					
					//added this to test locally cuz i cant get the email to link to localhost:5000
					if(response['status'] == 200 || response['status'] == 202){
						alert(response['message']);
						window.location.replace("/reset-password");
					}
					else{
						alert(response['message']);
						window.location.replace("/password");
					}
					 
				}
				else{
					// $('#reset-password-main-form').addClass("is-hidden");
					if(response['status'] == 200){
						$("#security-questions").removeClass("is-hidden");
						$("#send-email-reset").addClass("is-hidden");
						
						var question1 = response.one;
						var question2 = response.two;

						$('#question-1').append(question1);
						$('#question-2').append(question2);
					}
					else{
						alert(response['message']);
						window.location.replace("/password");
					}
				}
			},
			
			error: function (jqXHR, exception) {
				$body.removeClass("loading");
    			console.log("in error" + jqXHR);
    		}
		});

		return email;
	});

	// Check security questions in /password
	$('#security-questions').on('submit', function(){
		event.preventDefault();
		var that = $(this),
	      url = that.attr('action'),
	      type = that.attr('method'),
	      answer1Value = $("input[name='security-answer-1']").val();
	      answer2Value = $("input[name='security-answer-2']").val();
		  data = JSON.stringify({'email': email, 'answer1':answer1Value, 'answer2':answer2Value})
	      console.log(data);

		$.ajax(url, {
			type: type,
			data: data,
			contentType: 'application/json',
			dataType: 'json',

			success: function(response){
				$('#security-questions').addClass("is-hidden");

				if(response['status'] == 200){
					$('#password-has-been-reset-questions').removeClass('is-hidden');
					$('#password-has-been-reset-questions').append('<input type="hidden" name="account" value="' + response['account'] + '"/>');
				}
				else{
					$('#password-reset-failure').removeClass('is-hidden');
				}			
			
			},
			error: function(jqXHR, exception){
	      		console.log("error:");
	      		console.log(jqXHR);
	      		//display some error
	      	}
	    });
	});

	/*onlick for signature upload button*/
	$("#file-load-button").click(function () {
	    $("#file_input").click();
	});
});


/*checks that the passwords are the same*/
function checkPass() {
    //Store the password field objects into variables ...
    var pass1 = $('#pass1');
    var pass2 = $('#pass2');
    //Store the Confimation Message Object ...
    var message = $('#confirmMessage');
    //Remove Class
    $(message).removeClass('is-hidden');
    //Compare the values in the password field 
    //and the confirmation field
    if($(pass1).val() === $(pass2).val()){
        //The passwords match. 
        //Set the color to the good color and inform
        //the user that they have entered the correct password
		$(pass2).closest('.form-group').removeClass('has-error');
        $(message).removeClass('text-danger');
        //Add classes
        $(pass2).closest('.form-group').addClass('has-success');
        $(message).addClass('text-success');
        $(message).html('Passwords Match!');
    }else{
        //The passwords do not match.
        //Set the color to the bad color and
        //notify the user.
		$(pass2).closest('.form-group').removeClass('has-success');
        $(message).removeClass('text-success');
        //Add classes
        $(pass2).closest('.form-group').addClass('has-error');
        $(message).addClass('text-danger');
        $(message).html('Passwords Do Not Match!');
    }

}


