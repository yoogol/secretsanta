$(document).ready( function() {
    $('#myTable').DataTable({
        "paging": false,
        "bDestroy": true
    });
    $('[data-toggle="tooltip"]').tooltip()
})
