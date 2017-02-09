$(document).ready(function(){
	
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
	  			
				for (var i in response){
					if(i != 'status' && i != 'message'){
						var details = response[i].fname + " " + response[i].lname + " " +response[i].email;
						console.log(response[i].fname + " " + response[i].lname + " " +response[i].email);
						
						$("#choose-employee").append('<input type="radio" name="employee-to-get-award" value="'+i+'">' + details );
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
		$("#send-email-reset").removeClass("no-display");
		$("#display-security-questions").addClass("no-display");
		console.log("button pressed");
	});


	/* choosing to reset via email or password on /password*/
	$("#reset-password").on('submit', function(){
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
				console.log("sucess " + radioValue);
				if(radioValue == "email"){
					console.log("I will now display email stuff");
					$("#display-security-questions").addClass("no-display");
					$("#send-email-reset").removeClass("no-display");
				}
				else{
					console.log("I will now display security question stuff");
					$("#display-security-questions").removeClass("no-display");
					$("#send-email-reset").addClass("no-display");
				}


			},
			error: function (jqXHR, exception) {
    			console.log("in error" + jqXHR);
    		}
		});

		return false;
	});

	/*resetting password on /reset-password*/
	$('#password-has-been-reset').on('submit', function(){
		event.preventDefault();
		var that = $(this),
	      url = that.attr('action'),
	      type = that.attr('method'),
	      radioValue = $("input[name='account-type']:checked").val();
	      email = $("input[name='userName']").val();
	      password = $("input[name='password']").val();
	      code = $("input[name='reset-code']").val();
		  data = JSON.stringify({'email':email, 'account-type':radioValue, 'reset-code':code, 'password' :password});
	      console.log(data);

	      $.ajax(url, {
	      	type: type,
	      	data: data,
	      	contentType:'application/json',
	      	dataType: 'json',

	      	success: function(response){
	      		//display success you have reset your password, show login link
	      		$('#password-reset-sucess').removeClass('is-hidden');
	      	},
	      	error: function(jqXHR, exception){
	      		console.log("error:");
	      		console.log(jqXHR);
	      		//display some error
	      	}


	      });
	    return false;

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


