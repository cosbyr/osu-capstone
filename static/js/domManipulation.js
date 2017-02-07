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
	  			
				console.log(response[2].email);
				for (var i in response){
					var details = response[i].fname + " " + response[i].lname + " " +response[i].email;
					console.log(response[i].fname + " " + response[i].lname + " " +response[i].email);
					
					$("#choose-employee").append('<input type="radio" name="employee-to-get-award" value="'+i+'">' + details );
				}
				
		    },


		    // url: url,
		    // type: type,
		    // data: data,
		    // dataType: "json"

		    error: function (jqXHR, exception) {
		    	console.log("in error state");
		    	console.log(jqXHR.responseText);
    			console.log(jqXHR);
    // Your error handling logic here..
			}
	  	});
	  return false;
	});


	/* choosing to reset via email or password on /password*/
	$("#reset-password").on('submit', function(){
		event.preventDefault();
		var that = $(this),
	      url = that.attr('action'),
	      type = that.attr('method'),
	      radioValue = $("input[name='reset-method']:checked").val();
	      email = $("input[name='email']").val();
	      console.log(radioValue + " " + email + " " + url);
		

		$.ajax(url,{
			type: type,

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
});
