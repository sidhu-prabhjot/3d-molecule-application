/* javascript to accompany jquery.html */
$(document).ready( function() {

    /* add a click handler for our button */
    $("#button").click(
      function()
      {
	/* ajax post */
	$.post("/submit_handler.html",
	  /* pass a JavaScript dictionary */
	  {
	    name: $("#name").val(),	/* retreive value of name field */
	    extra_info: "some stuff here"
	  },
	  function( data, status )
	  {
	    alert( "Data: " + data + "\nStatus: " + status );
	  }
	);
      }
    );


	//send form data
	/* add a submit handler for our form */
	$("#element-form").submit(function(event) {
		/* prevent the default form submission behavior */
		event.preventDefault();
	
		/* get the form data */
		var formData = {
		"element-number": $("#element-number").val(),
		"element-code": $("#element-code").val(),
		"element-name": $("#element-name").val(),
		"color1": $("#color1").val(),
		"color2": $("#color2").val(),
		"color3": $("#color3").val(),
		"radius": $("#radius").val()
		};
	
		/* send an AJAX POST request */
		$.ajax({
		type: "POST",
		url: "/add_element_handler.html",
		data: formData,
		success: function(data) {
			/* handle success */
			alert("Element added successfully!");
		},
		error: function(xhr, status, error) {
			/* handle error */
			alert("Error adding element: " + error);
		}
		});
	});
  
	$("#upload-form").submit(function(event) {
		// Prevent the form from submitting normally
		event.preventDefault();
	  
		// Get the name data
		var nameData = {
		  "name": $("#name-input").val(),
		};
	  
		// Send the AJAX request to add the name
		var addNameRequest = $.ajax({
		  url: "/add_element_name.html",
		  type: "POST",
		  data: nameData,
		});
	  
		// Get the file data
		var fileData = new FormData();
		var fileInput = $("#file-input")[0];
		fileData.append("file", fileInput.files[0]);
	  
		// Send the AJAX request to upload the file
		addNameRequest.then(function() {
		  return $.ajax({
			url: "/sdf_upload.html",
			type: "POST",
			data: fileData,
			processData: false,
			contentType: false
		  });
		}).done(function(response) {
		  
			/* handle error */
			alert("File Uploaded Successfully! ");

		}).fail(function(xhr, status, error) {
		  
			/* handle error */
			alert("File Upload Failed! Make Sure File Is A Valid SDF File Or Check Name");

		});
	  });
	  
	  $('.delete-button').click(function() {
		var elementName = $('#element-name-delete').val();
	  
		$.ajax({
		  url: "/element_delete_handler.html",
		  type: "POST",
		  data: { element_name: elementName },
		  success: function(response) {
			
			/* handle error */
			alert(response);

		  },
		  error: function(jqXHR, textStatus, errorThrown) {
			
			/* handle error */
			alert("Element Deletion Failed");

		  }
		});
	  });


  }
);
  
  
  
  
  