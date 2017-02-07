$(document).ready(function(){
	
	/* for find employee form */
	$('#get-employee-form').on('submit', function(e){
	 
	  var that = $(this),
	      url = that.attr('action'),
	      type = that.attr('method'),
	      data = {};
	      console.log(url);

	  that.find('[name]').each(function(index, value) {
	    console.log(index)
	    var that = $(this),
	        name = that.attr('name'),
	        value = that.val();

	    data[name] = value;
	  });

	  $.ajax({
	  	
	    url: url,
	    type: type,
	    data: data,
	    success: function(response) {
	      console.log(response);
	    }


	  });
	  return false;
	});

});
