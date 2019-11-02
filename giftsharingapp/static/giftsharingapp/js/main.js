$(document).ready( function() {
    $('#friend-emails-field').keydown(function (e) {
        if(e.keyCode == 13) {
            e.preventDefault()
            return false;
        }
    })
    $('#myTable').DataTable({
        "pageLength": 100,
        "bDestroy": true
    });
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();

    // $('.group-dropdown').select2()
})

function dismissAlert(notification_id) {
    console.log(notification_id)
    let s = '#' + notification_id
    $.ajax({
        url: "/dismiss_notification",
        type: "POST",
        data: {
            notification_id: notification_id
        },
        success: function(data) {
            console.log(data)
            $(s).alert('close')
        }
    })

}

function acceptInvite(invite_id) {
    console.log("acceptInvite")
    console.log(invite_id)
    $.ajax({
        url: "/accept_invite/",
        type: "POST",
        data: {
            invite_id: invite_id
        },
        success: function(data) {
            $(".call-to-action").html(data.message)
            $(".accept-buttons").remove()
            $(".cancel-buttons").removeClass('hidden')

            // window.location.href = data.redirect_url;
        }
    })

}

function declineInvite(invite_id) {
    console.log("declineInvite")
    console.log(invite_id)
    $.ajax({
        url: "/decline_invite/",
        type: "POST",
        data: {
            invite_id: invite_id
        },
        success: function(data) {
            $(".call-to-action").html(data.message)
            $(".accept-buttons").remove()
            $(".cancel-buttons").removeClass('hidden')
        }
    })
}