google.charts.load('current', {packages: ['corechart','table']});

$(document).ready(function(){
	//all awards report (1)
	$('#all-awards-form').on('submit',function(){
		event.preventDefault();
		
		//clear report div
		$('#award-report').empty();
		
		var form = $(this);
		var url = form.attr('action');
		var type = form.attr('method');
		var reportType = $('#all-awards-report').val();
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
						dataTable.addColumn('number', 'Issued On');
						
						for(key in response){
							if(key != 'status'){
								dataTable.addRow([key,response[key]])
							}
						}
					});
					
					var chart = new google.visualization.PieChart(document.getElementById('award-report'));
					
					var options = {
						title: 'All Awards',
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
	
	
	//awards by manager report (2)
	$('#award-by-manager-form').on('submit',function(){
		event.preventDefault();
		
		//clear report div
		$('#award-report').empty();
		
		var form = $(this);
		var url = form.attr('action');
		var type = form.attr('method');
		var reportType = $('#award-by-manager').val();
		var data = JSON.stringify({'report':reportType});
		
		$.ajax(url, {
			type:type,
			data:data,
			contentType:'application/json',
			dataType:'json',
			
			success: function(response){
				if(response['status'] == 200){
					google.charts.setOnLoadCallback(function(){
						//create html to house manager table and award chart
						var htmlStr = '<table id="award-manager-table">' +
										'<tr>' +
										  '<td><div id="manager-table" style="border: 1px solid #ccc"></div></td>' +
										  '<td><div id="award-chart" style="border: 1px solid #ccc"></div></td>' +
										'</tr>' +
									  '</table>';
						$('#award-report').append(htmlStr);
						
						//init number of award types to display in award chart
						var lst = [];
						for(var i = 1; i < response['awards'][0].length - 1;i++){
							lst.push(0);
						}
						
						//generate manager table rows
						var managerTable = google.visualization.arrayToDataTable(response['managers']);
						
						//draw manager table
						var table = new google.visualization.Table(document.getElementById('manager-table'));
						table.draw(managerTable,{width:300,height:200});
						
						//set default award chart value
						var defaultData = google.visualization.arrayToDataTable([response['awards'][0],['Select Manager(s) From Table'].concat(lst).concat([''])]);
						
						//default award chart options
						chartOptions = {
							title:'Awards By Manager',
							legend: {position: 'top', maxLines: 3},
							bar: {groupWidth: '75%'},
							isStacked: true,
							width: 800,
							height: 400,
							vAxis: {title:'Number of Awards', minValue:0, maxValue:4, format:'0'},
							animation:{startup:true,duration:900}
						};
						
						//draw default award chart
						var chart = new google.visualization.ColumnChart(document.getElementById('award-chart'));
						chart.draw(defaultData,chartOptions);
						
						//add select event listener on manager table
						google.visualization.events.addListener(table, 'select', function(){
							//gets list of managers selected in the table
							var selection = table.getSelection();
							if(selection.length > 0){
								var managers = [];
								for(var i = 0; i < selection.length; i++){
									managers.push(managerTable.getFormattedValue(selection[i].row,0));
								}
								
								//get data for selected managers
								var newInfo = [response['awards'][0]];
								for(var i = 1; i < response['awards'].length; i++){
									if(managers.indexOf(response['awards'][i][0]) != -1){
										newInfo.push(response['awards'][i]);
									} 
								}
								
								//redraw award chart
								var chartData = google.visualization.arrayToDataTable(newInfo);
								chart = new google.visualization.ColumnChart(document.getElementById('award-chart'));
								chartOptions = {
									title:'Awards By Manager',
									legend: { position: 'top', maxLines: 3 },
									bar: { groupWidth: '75%' },
									isStacked: true,
									width: 800,
									height: 400,
									vAxis: {title:'Number of Awards',minValue:4, viewWindow:{min:0},format:'0'},
									animation:{startup:true,duration:900}
								};
								chart.draw(chartData,chartOptions);
								
								//clean up newInfo array
								newInfo.splice(1,newInfo.length);
							}
						});
					});
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



