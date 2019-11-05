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
    // $('[data-toggle="tooltip"]').tooltip();
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

function expandReceived(title) {
    let el = $('#received-gifts')
    // let title = $('#received-gifts-title')
    if (el.hasClass('hidden')) {
        title.html('Hide received gifts <i class="fas fa-caret-up"></i>');
        el.removeClass('hidden')
    } else {
        title.html('View received gifts <i class="fas fa-caret-down"></i>');
        el.addClass('hidden')
    }

}

function applyGiftFilter(friend_id, group_id, el) {
    console.log(friend_id, group_id)
    if (el.hasClass('btn-danger') || el.hasClass('btn-warning')) {
        console.log("Here")
        location.reload()
    }
    $.ajax({
        url: "/smart_santa_list_filter/",
        type: "GET",
        data: {
            friend_id: friend_id,
            group_id: group_id
        },
        success: function(data) {
            $('.group-button').each(function(i) {
                $(this).removeClass('btn-warning')
                $(this).addClass('btn-outline-warning')
            });
            $('.friend-button').each(function(i) {
                $(this).removeClass('btn-danger')
                $(this).addClass('btn-outline-danger')
            });
            if(friend_id) {
                el.removeClass('btn-outline-danger')
                el.addClass('btn-danger')
            } else if (group_id) {
                el.removeClass('btn-outline-warning')
                el.addClass('btn-warning')
            }

            $('#gift-list-cont').replaceWith(data)
        }
    })
}