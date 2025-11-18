const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

// Input and output directories
const inputDirectory = path.join(__dirname, '../static_src/img/');
const outputDirectory = path.join(__dirname, '../static_compiled/img/');

// Resizing constraints
const maxWidth = 1920;
const maxHeight = 1080;

// Ensure dirs exist
if (!fs.existsSync(outputDirectory)) {
  fs.mkdirSync(outputDirectory, { recursive: true });
}

// Get all files in the input directory
const files = fs.readdirSync(inputDirectory);

// Process each file and keep original extension/format
files.forEach((file) => {
  const ext = path.extname(file).toLowerCase();
  const inputPath = path.join(inputDirectory, file);
  const outputPath = path.join(outputDirectory, file);

  if (!ext.match(/\.(jpg|jpeg|png|gif)$/)) {
    return;
  }

  // GIFs: copy as-is (sharp cannot reliably write animated GIFs)
  if (ext === '.gif') {
    try {
      fs.copyFileSync(inputPath, outputPath);
      console.log(`Copied GIF without processing: ${file}`);
    } catch (err) {
      console.error(`Error copying ${file}: ${err}`);
    }
    return;
  }

  const pipeline = sharp(inputPath).resize(maxWidth, maxHeight, {
    fit: 'inside',
    withoutEnlargement: true,
  });

  // Keep format consistent with input extension
  if (ext === '.jpg' || ext === '.jpeg') {
    pipeline.jpeg({ quality: 80, progressive: true });
  } else if (ext === '.png') {
    pipeline.png({ compressionLevel: 9 });
  }

  pipeline.toFile(outputPath, (err) => {
    if (err) {
      console.error(`Error processing ${file}: ${err}`);
    } else {
      console.log(`Optimised ${file} -> ${outputPath}`);
    }
  });
});
