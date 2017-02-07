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
		  	dataType: 'json',
	  		success: function(data) {
		      console.log("passed through " + data);
		    },


		    // url: url,
		    // type: type,
		    // data: data,
		    // dataType: "json"

		    error: function(){
		    	console.log("sadly things didn't work as hoped" + data);
		    }
	  	});
	  return false;
	});


	/* choosing to reset via email or password on /password*/
	$("#reset-password").on('submit', function(){
		
		var that = $(this),
	      url = that.attr('action'),
	      type = that.attr('method'),
	      radioValue = $("input[name='reset-method']:checked").val();
	      console.log(radioValue);
		

		// $.ajax({


		// });

		return false;
	});
});
