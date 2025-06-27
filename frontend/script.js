// Detect if we're running locally
const isLocal = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";

// Auto-switch config between local dev and deployed Azure
const config = isLocal
  ? {
      functionsBase: "http://localhost:7071/api",
      blobUploads: "http://127.0.0.1:10000/devstoreaccount1/uploads/",
      blobTemp: "http://127.0.0.1:10000/devstoreaccount1/temp",
      blobOutput: "http://127.0.0.1:10000/devstoreaccount1/output/"
    }
  : {
      functionsBase: "https://Assignment2WatermarkingApp.azurewebsites.net/api",
      blobUploads: "https://watermarkuploads.blob.core.windows.net/uploads",
      blobTemp: "https://watermarktemp.blob.core.windows.net/temp",
      blobOutput: "https://watermarkoutput.blob.core.windows.net/output"
    };

// Upload a file to blob storage
async function uploadToBlob(file) {
  const blobName = Date.now() + "-" + file.name;
  const url = `http://localhost:7071/api/upload?name=${blobName}`;

  const response = await fetch(url, {
    method: "POST",
    body: file
  });

  if (!response.ok) {
    throw new Error("Upload failed: " + response.statusText);
  }

  // Return the blob path format your function expects
  return `blob://uploads/${blobName}`;
}

// Trigger thumbnail preview
async function generateThumbnail() {
  try {
    const videoFile = document.getElementById("videoInput").files[0];
    const imageFile = document.getElementById("imageInput").files[0];
    const workerCount = parseInt(document.getElementById("workerCount").value) || 1;

    if (!videoFile || !imageFile) {
      alert("Please upload both a video and watermark image.");
      return;
    }

    const videoPath = await uploadToBlob(videoFile);
    const imagePath = await uploadToBlob(imageFile);
    const outputName = `temp_thumbnail_${Date.now()}.png`;

    const data = {
      video_path: videoPath,
      watermark_path: imagePath,
      output_path: `${config.blobTemp}/${outputName}`,
      start_time: parseFloat(document.getElementById("startTime").value),
      end_time: parseFloat(document.getElementById("endTime").value),
      orientation: document.getElementById("orientation").value,
      opacity: parseFloat(document.getElementById("opacity").value),
      workers: workerCount,
      timestamp: 1.0
      
    };

    const response = await fetch(`${config.functionsBase}/requestthumbnail`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    

    // document.getElementById("previewImage").src = "https://placehold.co/600x400.png";

    if (response.ok) {
      document.getElementById("previewImage").src =
        `${config.blobOutput}/temp_thumbnail.png?t=${Date.now()}`; // force refresh
    } else {
      alert("Thumbnail generation failed.");
    }
  } catch (err) {
    console.error(err);
    alert("Error during thumbnail generation.");
  }
}

// Trigger final video rendering
async function renderFinal() {
  try {
    const videoFile = document.getElementById("videoInput").files[0];
    const imageFile = document.getElementById("imageInput").files[0];
    const workerCount = parseInt(document.getElementById("workerCount").value) || 1;

    if (!videoFile || !imageFile) {
      alert("Please upload both a video and watermark image.");
      return;
    }

    const videoPath = await uploadToBlob(videoFile);
    const imagePath = await uploadToBlob(imageFile);
    const outputName = `final_output_${Date.now()}.mp4`;

    const data = {
      video_path: videoPath,
      watermark_path: imagePath,
      output_path: `blob://output/${outputName}`,
      start_time: parseFloat(document.getElementById("startTime").value),
      end_time: parseFloat(document.getElementById("endTime").value),
      orientation: document.getElementById("orientation").value,
      opacity: parseFloat(document.getElementById("opacity").value),
      workers: workerCount
    };

    const response = await fetch(`${config.functionsBase}/requestwatermark`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      alert("Watermark render job queued. Check output folder shortly.");
    } else {
      alert("Render request failed.");
    }
  } catch (err) {
    console.error(err);
    alert("Error during render request.");
  }
}
