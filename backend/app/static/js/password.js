(function(){
  function generatePassword(length, useLetters=true, useDigits=true){
    const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const digits = '0123456789';
    let pool = '';
    if (useLetters) pool += letters;
    if (useDigits) pool += digits;
    if (!pool) pool = letters + digits;
    let out = '';
    const array = new Uint32Array(length);
    if (window.crypto && window.crypto.getRandomValues) {
      window.crypto.getRandomValues(array);
    } else {
      for (let i=0;i<length;i++) array[i] = Math.floor(Math.random()*0xffffffff);
    }
    for (let i=0;i<length;i++) out += pool[array[i] % pool.length];
    return out;
  }
  const genBtn = document.getElementById('gen');
  if (genBtn){
    genBtn.addEventListener('click', ()=>{
      const pwd = generatePassword(12, true, true);
      const input = document.getElementById('password');
      input.value = pwd;
    });
  }
})();
