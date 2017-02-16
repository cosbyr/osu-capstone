google.charts.load('current', {packages: ['corechart']});


$(document).ready(function(){
	//report 1
	$('#award-by-type-form').on('submit',function(){
		event.preventDefault();
		
		var form = $(this);
		var url = form.attr('action');
		var type = form.attr('method');
		var reportType = $('#award-by-type').val();
		var data = JSON.stringify({'report':reportType});
		console.log(data);
		
		$.ajax(url, {
			type:type,
			data:data,
			contentType:'application/json',
			dataType:'json',
			
			success: function(response){
				var dataTable;
				
				if(response['status'] == 200){
					google.charts.setOnLoadCallback(function(){
						dataTable = new google.visualization.DataTable();
						dataTable.addColumn('string', 'Award');
						dataTable.addColumn('number', 'Granted');
						
						for(key in response){
							if(key != 'status'){
								dataTable.addRow([key,response[key]])
							}
						}
					});
					
					var chart = new google.visualization.PieChart(document.getElementById('award-report'));
					
					var options = {
						title: 'Awards By Type'
					};
					
					chart.draw(dataTable,options);
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
	
	
	//report 2
	$('#award-by-manager-form').on('submit',function(){
		event.preventDefault();
		
		var form = $(this);
		var url = form.attr('action');
		var type = form.attr('method');
		var reportType = $('#award-by-manager').val();
		var data = JSON.stringify({'report':reportType});
		//test
		var pager = { currentPage: 0, countPages: 0, pageSize: 10 }; 
		
		$.ajax(url, {
			type:type,
			data:data,
			contentType:'application/json',
			dataType:'json',
			
			success: function(response){
				var types;
				var info = [];
				console.log('response:')
				console.log(response);
				if(response['status'] == 200){
					google.charts.setOnLoadCallback(function(){
						//data = new google.visualization.DataTable();
						types = response['types'];
						types.unshift('Type')
						types.push({role:'annotation'});
						info.push(types);
						for(element in response){
							var lst = [];
							if(element != 'status' && element != 'types'){
								lst.push(response[element]['name']);
								for(key in response[element]){
									if(key != 'name'){
										lst.push(response[element][key]);
									}
								}
								lst.push('');
								info.push(lst);
							}
						}
					});
					
					console.log('info:')
					console.log(info);
					
					var dataTable = google.visualization.arrayToDataTable(info);

					var options = {
						title:'Awards By Manager',
						legend: { position: 'top', maxLines: 3 },
						bar: { groupWidth: '75%' },
						isStacked: true,
					};
					
					var chart = new google.visualization.ColumnChart(document.getElementById('award-report'));
					chart.draw(dataTable,options);
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

