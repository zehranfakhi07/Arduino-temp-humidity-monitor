import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname } from 'node:path';

const port = process.env.PORT || 3000;

const mime = {
	'.html': 'text/html; charset=utf-8',
	'.css': 'text/css; charset=utf-8',
	'.js': 'text/javascript; charset=utf-8',
	'.json': 'application/json; charset=utf-8',
	'.png': 'image/png',
	'.jpg': 'image/jpeg',
	'.jpeg': 'image/jpeg',
	'.svg': 'image/svg+xml',
};

const server = http.createServer(async (req, res) => {
	try {
		const url = req.url === '/' ? '/index.html' : req.url;
		const filePath = new URL(`./public${url}`, import.meta.url);
		const data = await readFile(filePath);
		const type = mime[extname(filePath.pathname)] || 'text/plain; charset=utf-8';
		res.writeHead(200, { 'Content-Type': type });
		res.end(data);
	} catch (err) {
		res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
		res.end('Not found');
	}
});

server.listen(port, () => {
	console.log(`Server running on http://localhost:${port}`);
});
