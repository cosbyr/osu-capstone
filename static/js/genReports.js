google.charts.load('current', {packages: ['corechart','table','calendar']});

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
							//remove calendar chart
							if($('#calendar-chart').length){
								$('#calendar-chart').remove();
								$('.chart-separator').remove();
							}
									
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
								
								//add select event to bar chart
								google.visualization.events.addListener(chart, 'select', function(){
									
									//reset calendar chart
									if($('#calendar-chart').length){
										$('#calendar-chart').remove();
										$('.chart-separator').remove();
									}
									
									//response['dates'] index constants
									const FNAME_INDEX = 0;
									const LNAME_INDEX = 1;
									const TYPE_INDEX = 2;
									const DATE_INDEX = 3;
									const COUNT_INDEX = 4;
									
									//get selection data
									let selection = chart.getSelection();
									if(selection.length > 0){
										let managerName = chartData.getFormattedValue(selection[0].row,0);
										let awardType = chartData.getColumnLabel(selection[0].column);
										console.log(managerName + ' ' + awardType);
										
										//create html to display chart
										$('#award-report').after("<br class='chart-separator'><br class='chart-separator'><div id='calendar-chart'></div>");
										
										//init chart and data table
										let calendarChartDataTable = new google.visualization.DataTable();
										let calendarChart = new google.visualization.Calendar(document.getElementById('calendar-chart'));
										
										//create chart header
										calendarChartDataTable.addColumn({type:'date',id:'Date' });
										calendarChartDataTable.addColumn({type:'number',id:'Awards granted' });
										
										//add data to table
										var years = []
										for(var i = 0; i < response['dates'].length; i++){
											//console.log(new Date(response['dates'][i][DATE_INDEX]));
											let curName = response['dates'][i][FNAME_INDEX] + ' ' + response['dates'][i][LNAME_INDEX];
											let curType = response['dates'][i][TYPE_INDEX];
											if((curName === managerName) && (curType === awardType)){
												//convert date to milliseconds
												let date = new Date(Date.parse(response['dates'][i][DATE_INDEX]));
												
												//get UTC year, month and day
												//this has to be done because js assumes the date object in the GMT tz and converts to the browser's tz
												let year = date.getUTCFullYear();
												let month = date.getUTCMonth();
												let day = date.getUTCDate();
												
												if(years.indexOf(year) < 0){
													years.push(year);
												}
												//create a new date object and pass it to the calendar chart
												date = new Date(year,month,day);
												calendarChartDataTable.addRow([date,response['dates'][i][COUNT_INDEX]]);
											}
										}
										
										//draw chart
										var options = {
											title: awardType,
											height: years.length * 200,
											noDataPattern: {
												backgroundColor: '#ffffff',
												color: '#dbedda'
											 },
											 colorAxis: {
												minValue: 0,  colors: ['#9bffe6', '#0645aa']
											}
										};

										calendarChart.draw(calendarChartDataTable, options);
									}
								});
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
	
	//awards by employee report (3)
	$('#award-by-employee-form').on('submit',function(){
		event.preventDefault();
		
		//clear report div
		$('#award-report').empty();
		
		var form = $(this);
		var url = form.attr('action');
		var type = form.attr('method');
		var reportType = $('#award-by-employee').val();
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
						var htmlStr = '<table id="award-employee-table">' +
										'<tr>' +
										  '<td><div id="employee-table" style="border: 1px solid #ccc"></div></td>' +
										  '<td><div id="award-chart" style="border: 1px solid #ccc"></div></td>' +
										'</tr>' +
									  '</table>';
						$('#award-report').append(htmlStr);
						
						//init number of award types to display in award chart
						var lst = [];
						for(var i = 1; i < response['awards'][0].length - 1;i++){
							lst.push(0);
						}
						
						//generate employee table rows
						var employeeTable = google.visualization.arrayToDataTable(response['employees']);
						
						//draw manager table
						var table = new google.visualization.Table(document.getElementById('employee-table'));
						table.draw(employeeTable,{width:300,height:200});
						
						//set default award chart value
						var defaultData = google.visualization.arrayToDataTable([response['awards'][0],['Select Employees(s) From Table'].concat(lst).concat([''])]);
						
						//default award chart options
						chartOptions = {
							title:'Awards By Employees',
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
						
						//add select event listener on employee table
						google.visualization.events.addListener(table, 'select', function(){
							//gets list of employees selected in the table
							var selection = table.getSelection();
							if(selection.length > 0){
								var employees = [];
								for(var i = 0; i < selection.length; i++){
									employees.push(employeeTable.getFormattedValue(selection[i].row,0));
								}
								
								//get data for selected employees
								var newInfo = [response['awards'][0]];
								for(var i = 1; i < response['awards'].length; i++){
									if(employees.indexOf(response['awards'][i][0]) != -1){
										newInfo.push(response['awards'][i]);
									} 
								}
								
								//redraw award chart
								var chartData = google.visualization.arrayToDataTable(newInfo);
								chart = new google.visualization.ColumnChart(document.getElementById('award-chart'));
								chartOptions = {
									title:'Awards By Employee',
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



