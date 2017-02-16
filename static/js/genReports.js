google.charts.load('current', {packages: ['corechart']});


$(document).ready(function(){
	$('#award-by-type-form').on('submit',function(){
		event.preventDefault();
		
		var form = $(this);
		var url = form.attr('action');
		var type = form.attr('method');
		var reportType = $("input[name='award-by-type']").val();
		var data = JSON.stringify({'report':reportType});
		console.log(data);
		
		$.ajax(url, {
			type:type,
			data:data,
			contentType:'application/json',
			dataType:'json',
			
			success: function(response){
				var data;
				console.log(response);
				if(response['status'] == 200){
					google.charts.setOnLoadCallback(function(){
						data = new google.visualization.DataTable();
						data.addColumn('string', 'Award');
						data.addColumn('number', 'Granted');
						
						for(key in response){
							if(key != 'status'){
								data.addRow([key,response[key]])
							}
						}
					});
					
					var chart = new google.visualization.PieChart(document.getElementById('award-by-type-report'));
					chart.draw(data);
				}
				else{
					alert('Unable to generate report.');
				}
				
				
				
			},
			error: function(jqXHR,exception){
				console.log('error:');
				console.log(jqXHR);
			}
		});
	});
});

