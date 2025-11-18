const fs = require('fs');
const { spawn } = require('child_process');

const cmd = process.platform === 'win32' ? 'python' : 'python3';

function run() {
  spawn(cmd, ['manage.py', 'collectstatic', '--noinput'], { stdio: 'inherit' });
}

let pending = false;

fs.watch('static_compiled', { recursive: true }, () => {
  if (pending) return;
  pending = true;
  setTimeout(() => {
    pending = false;
    run();
  }, 200);
});

console.log('watching static_compiled for collectstatic');
run();