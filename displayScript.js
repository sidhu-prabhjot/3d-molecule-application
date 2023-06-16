/* javascript to accompany jquery.html */
var molToRotate;
$(document).ready( 
    /* this defines a function that gets called after the document is in memory */
    function() {
      $.ajax({
        url: "/molecule_list.html",
        type: "GET",
        dataType: "text",
        success: function(data) {
          var moleculeNames = data.trim().split("\n");
  
          // Create a button for each molecule name
          $.each(moleculeNames, function(index, name) {
            var button = $("<button>", {
              text: name,
              value: name,
              class: "list-btn"
            });

            // Attach a click listener to the button
            button.click(function() {
                var uniqueValue = $(this).val();
                var buttonEl = $(this);
                molToRotate = uniqueValue;

                $(".molecule-data").remove();
                $(".load-svg-btn").remove();
                
                // Make a POST request with the unique value
                $.ajax({
                url: "/molecule_data.html",
                type: "POST",
                data: { data: uniqueValue },
                dataType: "text",
                success: function(response) {
                    // Create a new element to hold the response text
                    var responseEl = $("<p>", {
                        text: response,
                        class: "molecule-data"
                    });

                    console.log(response);

                    // Create a new button to load the SVG
                    var svgButton = $("<button>", {
                        text: "Load SVG",
                        class: "load-svg-btn"
                    });

                    // Attach a click listener to the SVG button
                    svgButton.click(function() {
                        var moleculeName = buttonEl.val();

                        // Make a POST request with the molecule name
                        $.ajax({
                        url: "/molecule_svg.html",
                        type: "POST",
                        data: { data: moleculeName },
                        dataType: "",
                        success: function(svgString) {
                            // Create a new element to hold the SVG
                            var svgEl = $("<div>", {
                                html: svgString
                            });

                            var svg = svgEl.find("svg")[0];

                            // Remove the height and width attributes
                            svg.removeAttribute('width');
                            svg.removeAttribute('height');

                            // Add the viewBox and preserveAspectRatio attributes
                            svg.setAttribute('viewBox', '0 0 1000 1000');
                            svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

                            $("#svg-container").empty().append(svgEl);

                            $("#rotate-btn").show();
                            $("#rotate-form-container").show();
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            console.error(textStatus, errorThrown);
                        }
                        });
                    });

                    // Insert the response element and SVG button after the button
                    buttonEl.after(responseEl, svgButton);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.error(textStatus, errorThrown);
                }
                });
            });
            // Append the button to the document
            $("#molecule-btn-container").append(button);
          }); // <- Add closing parenthesis here
        },
        error: function(jqXHR, textStatus, errorThrown) {
          console.error(textStatus, errorThrown);
        }
      });


      // Set up the "Rotate" button click listener
    $("#rotate-btn").click(function() {
        // Get the input values
        var x = $("#x-input").val() || 0;
        var y = $("#y-input").val() || 0;
        var z = $("#z-input").val() || 0;

        console.log("Name of molecule that is going to be rotated: " + molToRotate);

        // Send the AJAX request to /molecule_rotate.html
        $.ajax({
        url: "/molecule_rotate.html",
        type: "POST",
        data: { x: x, y: y, z: z, name:molToRotate},
        dataType: "html",
        success: function(response) {

            var parser = new DOMParser();
            var svg = parser.parseFromString(response, "image/svg+xml").querySelector("svg");

            // Remove the height and width attributes
            svg.removeAttribute('width');
            svg.removeAttribute('height');

            // Add the viewBox and preserveAspectRatio attributes
            svg.setAttribute('viewBox', '0 0 1000 1000');
            svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
            // Insert the response HTML into the SVG container
            $("#svg-container").empty().append(svg);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            alert("Please Enter Some Values");
        }
        });
    });

    $("#rotate-btn").hide();
    $("#rotate-form-container").hide();

    // Set up the input value change listeners
    $("input[type='number']").change(function() {
        // If one of the input values is set, set the other two to 0
        var $input = $(this);
        var value = $input.val();
        if (value !== "") {
        $("input[type='number']").not($input).val(0);
        }
    });
    }
  );
  
    
    
    
    
    