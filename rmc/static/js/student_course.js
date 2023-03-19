var cousre_id;

function bindBtnAddEvent(cousreId) {
    cousre_id = cousreId;
    // Clear data in the box
    $("#formAdd")[0].reset();

    // Set the title of the box
    $("#myModalLabel").text("Add Comment");

    // Click on the comment button to display the box.
    $('#myModal').modal('show');
}


function doAdd() {
    $(".error-msg").empty();

    // Sending requests to the backend
    $.ajax({
        //Transfer the form data with id=formAdd and the value of uid
        url: "/student/addcomment/" + "?uid=" + cousre_id,
        type: "post",
        data: $("#formAdd").serialize(),

        dataType: "JSON",
        success: function (res) {

            if (res.status) {

                // Clear the form
                $("#formAdd")[0].reset();

                // Close the box
                $('#myModal').modal('hide');

                location.reload();

            } else {
                // Display the error message in the box.
                $.each(res.error, function (name, errorList) {
                    $("#id_" + name).next().text(errorList[0]);
                })
            }
        }
    })
}
