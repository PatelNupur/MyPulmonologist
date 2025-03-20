// Design By
// - https://dribbble.com/shots/13992184-File-Uploader-Drag-Drop

// Select Upload-Area
const uploadArea = document.querySelector('#uploadArea')

// Select Drop-Zoon Area
const dropZoon = document.querySelector('#dropZoon');

// Loading Text
const loadingText = document.querySelector('#loadingText');

// Slect File Input 
const fileInput = document.querySelector('#fileInput');

// Select Preview Image
const previewImage = document.querySelector('#previewImage');

// File-Details Area
const fileDetails = document.querySelector('#fileDetails');

// Uploaded File
const uploadedFile = document.querySelector('#uploadedFile');

// Uploaded File Info
const uploadedFileInfo = document.querySelector('#uploadedFileInfo');

// Uploaded File  Name
const uploadedFileName = document.querySelector('.uploaded-file__name');

// Uploaded File Icon
const uploadedFileIconText = document.querySelector('.uploaded-file__icon-text');

// Uploaded File Counter
const uploadedFileCounter = document.querySelector('.uploaded-file__counter');

// ToolTip Data
const toolTipData = document.querySelector('.upload-area__tooltip-data');

// Images Types
const imagesTypes = [
  "jpeg",
  "jpg",
  "png",
];

// Append Images Types Array Inisde Tooltip Data
toolTipData.innerHTML = [...imagesTypes].join(', .');

// When (drop-zoon) has (dragover) Event 
dropZoon.addEventListener('dragover', function (event) {
  // Prevent Default Behavior 
  event.preventDefault();

  // Add Class (drop-zoon--over) On (drop-zoon)
  dropZoon.classList.add('drop-zoon--over');
});

// When (drop-zoon) has (dragleave) Event 
dropZoon.addEventListener('dragleave', function (event) {
  // Remove Class (drop-zoon--over) from (drop-zoon)
  dropZoon.classList.remove('drop-zoon--over');
});

// When (drop-zoon) has (drop) Event 
dropZoon.addEventListener('drop', function (event) {
  
  // Prevent Default Behavior 
  event.preventDefault();
  $('#btn-predict').show();
  // Remove Class (drop-zoon--over) from (drop-zoon)
  dropZoon.classList.remove('drop-zoon--over');
  
  // Select The Dropped File
  const file = event.dataTransfer.files[0];

  // Call Function uploadFile(), And Send To Her The Dropped File :)
  uploadFile(file);

});

// When (drop-zoon) has (click) Event 
dropZoon.addEventListener('click', function (event) {
  // Click The (fileInput)
  fileInput.click();
});

// When (fileInput) has (change) Event 
fileInput.addEventListener('change', function (event) {
  // Select The Chosen File
  const file = event.target.files[0];

  // Call Function uploadFile(), And Send To Her The Chosen File :)
  uploadFile(file);
});

// Upload File Function
function uploadFile(file) {
  // FileReader()
  const fileReader = new FileReader();
  // File Type 
  const fileType = file.type;
  // File Size 
  const fileSize = file.size;

  // If File Is Passed from the (File Validation) Function
  if (fileValidate(fileType, fileSize)) {
    // Add Class (drop-zoon--Uploaded) on (drop-zoon)
    dropZoon.classList.add('drop-zoon--Uploaded');

    // Show Loading-text
    loadingText.style.display = "block";
    // Hide Preview Image
    previewImage.style.display = 'none';

    // Remove Class (uploaded-file--open) From (uploadedFile)
    uploadedFile.classList.remove('uploaded-file--open');
    // Remove Class (uploaded-file__info--active) from (uploadedFileInfo)
    uploadedFileInfo.classList.remove('uploaded-file__info--active');

    // After File Reader Loaded 
    fileReader.addEventListener('load', function () {
      // After Half Second 
      setTimeout(function () {
        // Add Class (upload-area--open) On (uploadArea)
        uploadArea.classList.add('upload-area--open');

        // Hide Loading-text (please-wait) Element
        loadingText.style.display = "none";
        // Show Preview Image
        previewImage.style.display = 'block';

        // Add Class (file-details--open) On (fileDetails)
        fileDetails.classList.add('file-details--open');
        // Add Class (uploaded-file--open) On (uploadedFile)
        uploadedFile.classList.add('uploaded-file--open');
        // Add Class (uploaded-file__info--active) On (uploadedFileInfo)
        uploadedFileInfo.classList.add('uploaded-file__info--active');
      }, 500); // 0.5s

      // Add The (fileReader) Result Inside (previewImage) Source
      previewImage.setAttribute('src', fileReader.result);

      // Add File Name Inside Uploaded File Name
      uploadedFileName.innerHTML = file.name;

      // Call Function progressMove();
      progressMove();
    });

    // Read (file) As Data Url 
    fileReader.readAsDataURL(file);
    
  } else { // Else

    this; // (this) Represent The fileValidate(fileType, fileSize) Function

  };
};

// Progress Counter Increase Function
function progressMove() {
  // Counter Start
  let counter = 0;

  // After 600ms 
  setTimeout(() => {
    // Every 100ms
    let counterIncrease = setInterval(() => {
      // If (counter) is equle 100 
      if (counter === 100) {
        // Stop (Counter Increase)
        clearInterval(counterIncrease);
      } else { // Else
        // plus 10 on counter
        counter = counter + 10;
        // add (counter) vlaue inisde (uploadedFileCounter)
        uploadedFileCounter.innerHTML = `${counter}%`
      }
    }, 100);
  }, 600);
};


// Simple File Validate Function
function fileValidate(fileType, fileSize) {
  // File Type Validation
  let isImage = imagesTypes.filter((type) => fileType.indexOf(`image/${type}`) !== -1);

  // If The Uploaded File Type Is 'jpeg'
  if (isImage[0] === 'jpeg') {
    // Add Inisde (uploadedFileIconText) The (jpg) Value
    uploadedFileIconText.innerHTML = 'jpg';
  } else { // else
    // Add Inisde (uploadedFileIconText) The Uploaded File Type 
    uploadedFileIconText.innerHTML = isImage[0];
  };

  // If The Uploaded File Is An Image
  if (isImage.length !== 0) {
    // Check, If File Size Is 2MB or Less
    if (fileSize <= 20000000) { // 2MB :)
      return true;
    } else { // Else File Size
      return alert('Please Your File Should be 2 Megabytes or Less');
    };
  } else { // Else File Type 
    return alert('Please make sure to upload An Image File Type');
  };
};

// :)

function readURL(input) {
  if (input.files && input.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
          $('#imagePreview').css('background-image', 'url(' + e.target.result + ')');
          $('#imagePreview').hide();
          $('#imagePreview').fadeIn(650);
      }
      reader.readAsDataURL(input.files[0]);
  }
}

$("#fileInput").change(function () {
  $('#btn-predict').show();
  readURL(this);
});     


$('#btn-predict').click(function () {
  var form_data = new FormData($('#upload-file')[0]); 

  // Show loading animation
  $(this).hide();
  $('.loader').show();

  // Make prediction by calling api /predict
  $.ajax({
      type: 'POST',
      url: '/predict',
      data: form_data,
      contentType: false,
      cache: false,
      processData: false,
      async: true,
      success: function (data) {
          // Get and display the result
          $('.loader').hide();
          $('#result').fadeIn(600);
          $('#result').text(' Result:  ' + data);
          console.log('Success!');
//       },
//   });
// });


// // Show the feedback button after receiving a result
// $('#btn-predict').click(function () {
//     var form_data = new FormData($('#upload-file')[0]);

//     // Show loading animation
//     $(this).hide();
//     $('.loader').show();

//     // Make prediction by calling API /predict
//     $.ajax({
//         type: 'POST',
//         url: '/predict',
//         data: form_data,
//         contentType: false,
//         cache: false,
//         processData: false,
//         async: true,
//         success: function (data) {
//             $('.loader').hide();
//             $('#result').fadeIn(600);
//             $('#result').text('Result: ' + data);
//             console.log('Success!');

            // Show the feedback button
            $('#feedback-btn').show();
        },
    });
});

// Show feedback form when clicking the button
$('#feedback-btn').click(function () {
    $('#feedback-form').show();
});

// Submit feedback
$('#submit-feedback').click(function () {
    var feedbackText = $('#feedback-text').val();
    var prediction = $('#result').text().replace('Result: ', '');

    $.ajax({
        type: 'POST',
        url: '/submit_feedback',
        data: JSON.stringify({ prediction: prediction, feedback: feedbackText }),
        contentType: 'application/json',
        success: function (response) {
            alert(response.message);  // Show confirmation
            $('#feedback-form').hide();  // Hide form after submission
        }
    });
});


$(document).ready(function() {
  // Assuming the result is ready and you want to show the feedback button
  $('#btn-predict').on('click', function() {
      // Show the feedback button after prediction is done
      $('#feedback-btn').show();
  });

  // When "Give Feedback" button is clicked, show the feedback form and overlay
  $('#feedback-btn').on('click', function() {
      $('#feedback-form').fadeIn();  // Fade-in the feedback form
      $('#feedback-overlay').fadeIn();  // Fade-in the overlay
  });

  // When the overlay is clicked, hide the feedback form and overlay
  $('#feedback-overlay').on('click', function() {
      $('#feedback-form').fadeOut();  // Fade-out the feedback form
      $('#feedback-overlay').fadeOut();  // Fade-out the overlay
  });

  // Handle feedback submission
  $('#submit-feedback').on('click', function() {
      var feedback = $('#feedback-text').val();
      
      // Handle feedback submission logic (like sending it to the server)
      if(feedback) {
          alert('Thank you for your feedback!');
          $('#feedback-form').fadeOut();  // Hide the feedback form after submission
          $('#feedback-overlay').fadeOut();  // Hide the overlay
      } else {
          alert('Please provide feedback before submitting.');
      }
  });
});
