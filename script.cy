v = choose(EAGLView)[0]

function CGPointMake(x, y) { 
	return {x:x, y:y}; 
}

function createTouch(x, y) {
	touch = [[UITouch alloc] init];
	
	touch->_view = v;
	touch->_window = v.window;
	
	touch->_locationInWindow = CGPointMake(x,y);

	return touch;
}

function startTouch(touch) {
	[v touchesBegan: [NSSet setWithArray:[touch]] withEvent: nil];
}

function endTouch(touch) {
	[v touchesEnded: [NSSet setWithArray:[touch]] withEvent: nil];
}

function sendTouch(touch) {
	startTouch(touch);
	endTouch(touch);
}

function touchAt(x, y) {
	sendTouch(createTouch(x, y));
}

