
var columnDefs = [
    {field: 'sym', suppressCellFlash: true},
    {field: 'quote ', suppressCellFlash: true},
    {field: 'bid'},
    {field: 'bidqty'},
    {field: 'ask'},
    {field: 'askqty'}
];

//base,pbid,pask,minasksym,minasksym

var arbcolumnDefs = [
    {field: 'base', suppressCellFlash: true},
    {field: 'pask'},
    {field: 'minasksym'},
    {field: 'maxasksym'}
];

// placing in 13 rows, so there are exactly enough rows to fill the grid, makes
// the row animation look nice when you see all the rows
var dataSet;

var gridOptions = {
    columnDefs: columnDefs,
    rowData: [],
    pinnedTopRowData: [],
    pinnedBottomRowData: [],
    enableCellChangeFlash: true,
    enableColResize: true,
    enableSorting: true,
    refreshCells: true,
    getRowNodeId: function(data) { return data.sym; },
    deltaRowDataMode: true,
    onGridReady: function (params) {
        params.api.setRowData(dataSet);
      //  params.api.setPinnedTopRowData(topRowData);
      //  params.api.setPinnedBottomRowData(bottomRowData);
    },
    onFirstDataRendered(params) {
        params.api.sizeColumnsToFit();
    }
};



var arbgridOptions = {
    columnDefs: arbcolumnDefs,
    rowData: [],
    pinnedTopRowData: [],
    pinnedBottomRowData: [],
    enableCellChangeFlash: true,
    enableColResize: true,
    enableSorting: true,
    refreshCells: true,
    getRowNodeId: function(data) { return data.base; },
    deltaRowDataMode: true,
    onGridReady: function (params) {
        params.api.setRowData(dataSet);

    },
    onFirstDataRendered(params) {
        params.api.sizeColumnsToFit();
    }
};


// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {
    connect();
    var gridDiv = document.querySelector('#pxgrid');
    new agGrid.Grid(gridDiv, gridOptions);
    var arbgridDiv = document.querySelector('#arbgrid');
    new agGrid.Grid(arbgridDiv, arbgridOptions);
});



function connect(){
      if ("WebSocket" in window){ // check if WebSockets supported
          // open a WebSocket
          var ws = new WebSocket("ws://localhost:5001");
          ws.onopen = function(){
              console.log('connected')

                    $("#connection").removeClass("btn-danger").addClass("btn-success");
                    $("#connection").html('CONNECTED');

          };
          ws.onmessage = function(msg){
            dataString = msg.data
           var obj = JSON.parse(dataString)

           //dataSet = JSON.parse(obj);

           if ((typeof obj) == "string")

           {dataSet = JSON.parse(obj);}
           else {
               dataSet = obj
           }
             if(dataString.includes("minasksym"))
             {
                 arbgridOptions.api.setRowData(dataSet)
             }
             else{
                gridOptions.api.setRowData(dataSet)
             }

          };
          ws.onclose = function(){
              // called when WebSocket is closed
          };
      }
      else {
          // the browser doesn't support WebSockets
      }
  }

  function onFilterTextBoxChanged() {
      gridOptions.api.setQuickFilter(document.getElementById('filter-text-box').value);
  }
