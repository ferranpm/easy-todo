function toggle(e, tr) {
    e.stopPropagation();
    var ch = tr.find('input[type="checkbox"]');
    var item_id = tr.data('itemid');
    var list_id = tr.data('listid');
    if (tr.hasClass('done')) {
        jQuery.post('/unmark/' + list_id + '/' + item_id, document.cookie);
        tr.removeClass('done');
        ch.prop('checked', false);
    }
    else {
        jQuery.post('/mark/' + list_id + '/' + item_id, document.cookie);
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
