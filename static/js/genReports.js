google.charts.load('current', {packages: ['corechart','table']});
/*
google.charts.setOnLoadCallback(drawAllAwards);
google.charts.setOnLoadCallback(drawAwardsByManager);
google.charts.setOnLoadCallback(drawAwardsByEmployee);
google.charts.setOnLoadCallback(drawAwardsByDate);

function drawAllAwards(){
	
}

function drawAwardsByManager(){
	
}

function drawAwardsByEmployee(){
	
}

function drawAwardsByDate(){
	
}
*/

$(document).ready(function(){
	//all awards report
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
	
	
	//awards by manager report
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
				var table;
				var chart;
				var chartOptions;
				var types;
				var info = [];
				var managerData = new google.visualization.DataTable();
				managerData.addColumn('string', 'Name');
				managerData.addColumn('string', 'Title');
				
				if(response['status'] == 200){
					google.charts.setOnLoadCallback(function(){
						
						//form data object out of response for arrayToDataTable() function
						types = response['types'];
						types.unshift('Type')
						types.push({role:'annotation'});
						info.push(types);
						
						for(element in response){
							if(element != 'status' && element != 'types'){
								managerData.addRow([response[element]['name'],response[element]['title']]);
							}
						}
						/*for(element in response){
							var lst = [];

							if(element != 'status' && element != 'types'){
								lst.push(response[element]['name']);
								managerData.addRow([response[element]['name'],response[element]['title']]);
								
								for(key in response[element]){
									if(key != 'name' && key != 'title'){
										lst.push(response[element][key]);
									}
								}
								lst.push('');
								info.push(lst);
							}
						}*/
						//-------------------------------------------------------------------------------
						
						//set default award chart value
						var defaultData = google.visualization.arrayToDataTable([info[0],['Select Manager(s) From Table',0,0,'']]);
						
						//award chart options
						chartOptions = {
							title:'Awards By Manager',
							legend: { position: 'top', maxLines: 3 },
							bar: { groupWidth: '75%' },
							isStacked: true,
							width: 800,
							height: 400,
							vAxis: {title:'Number of Awards', minValue:0, maxValue:4, format:'0'},
							animation:{startup:true,duration:900}
						};
						
						//create html to house manager table and award chart
						var htmlStr = '<table id="award-manager-table">' +
										'<tr>' +
										  '<td><div id="manager-table" style="border: 1px solid #ccc"></div></td>' +
										  '<td><div id="award-chart" style="border: 1px solid #ccc"></div></td>' +
										'</tr>' +
									  '</table>';
						$('#award-report').append(htmlStr);
						
						//draw manager table
						table = new google.visualization.Table(document.getElementById('manager-table'));
						table.draw(managerData,{width:300,height:200});
						
						//draw default award chart
						chart = new google.visualization.ColumnChart(document.getElementById('award-chart'));
						chart.draw(defaultData,chartOptions);
					});
					
					console.log('info:');
					console.log(info);
					console.log('manager data:');
					console.log(managerData);
					
					//add select event listener on manager table
					//gets list of managers selected in the table
					google.visualization.events.addListener(table, 'select', function(){
						var selection = table.getSelection();
						if(selection.length > 0){
							var managers = [];
							for(var i = 0; i < selection.length; i++){
								managers.push(managerData.getFormattedValue(selection[i].row,0));
							}
							
							for(element in response){
								var lst = [];

								if(element != 'status' && element != 'types'){
									if(managers.indexOf(response[element]['name']) != -1){
										lst.push(response[element]['name']);
										
										for(key in response[element]){
											if(key != 'name' && key != 'title'){
												lst.push(response[element][key]);
											}
										}
										lst.push('');
										info.push(lst);
									}
								}
							}
							
							//redraw award chart
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
							var chartData = google.visualization.arrayToDataTable(info);
							chart = new google.visualization.ColumnChart(document.getElementById('award-chart'));
							chart.draw(chartData,chartOptions);
							
							//clean up info array
							info.splice(1,info.length);
						}
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



