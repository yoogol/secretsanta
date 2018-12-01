$(document).ready( function() {
    $('#myTable').DataTable({
        "pageLength": 100,
        "bDestroy": true
    });
    $('[data-toggle="tooltip"]').tooltip()
})
