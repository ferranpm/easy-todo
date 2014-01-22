function toggle(e) {
    e.stopPropagation();
    var tr = $(e.target).closest('tr');
    var ch = tr.find('input[type="checkbox"]');
    var id = tr.data('id');
    if (tr.hasClass('done')) {
        jQuery.post('/unmark/' + id);
        tr.removeClass('done');
        ch.prop('checked', false);
    }
    else {
        jQuery.post('/mark/' + id);
        tr.addClass('done');
        ch.prop('checked', true);
    }
}

function a_handler(e) {
    e.stopPropagation();
}

function check_delete() {
    return confirm("Are you sure you want to delete the list?");
}
