"""Çalışan TTS'e Lua gönderir, cevabı yazdırır (External Editor API).

TTS 39999'u dinler, cevapları 39998'e yollar; bu yüzden önce 39998'de dinlemeye başlayıp
sonra komutu gönderiyoruz. Kullanım: python3 tts_api.py 'return #getObjects()'
"""
import json, socket, sys, threading

def run(script, timeout=8.0):
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 39998)); srv.listen(5); srv.settimeout(timeout)
    msgs = []
    def listen():
        try:
            while True:
                c, _ = srv.accept(); buf = b""
                while chunk := c.recv(65536): buf += chunk
                c.close()
                # TTS her mesajı girintili (çok satırlı) JSON olarak yollar; satır satır
                # bölmek bozuyordu, bütün tamponu sırayla çözüyoruz.
                text = buf.decode("utf-8", "replace").strip()
                dec, i = json.JSONDecoder(), 0
                while i < len(text):
                    obj, i = dec.raw_decode(text, i)
                    msgs.append(obj)
                    while i < len(text) and text[i].isspace(): i += 1
                # Global betikte "return" mesajı (5) gelmiyor, sadece print (2) ve hata (3)
                # geliyor; ilk mesajdan sonra kısa sessizlik = bitti.
                srv.settimeout(1.5)
        except socket.timeout:
            pass
    t = threading.Thread(target=listen); t.start()
    s = socket.create_connection(("127.0.0.1", 39999), timeout=3)
    # Sonucu print ile geri al: return değeri API'den dönmüyor.
    wrapped = "local __r = (function() " + script + " end)() if __r ~= nil then print(tostring(__r)) end"
    s.sendall(json.dumps({"messageID": 3, "guid": "-1", "script": wrapped}).encode()); s.close()
    t.join(); srv.close()
    return msgs

if __name__ == "__main__":
    for m in run(sys.argv[1]):
        print(json.dumps(m, ensure_ascii=False)[:4000])
