// This is the js for the default/index.html view.

var app = function () {

	var self = {};

	Vue.config.silent = false; // show all warnings

	// Extends an array
	self.extend = function (a, b) {
		for (var i = 0; i < b.length; i++) {
			a.push(b[i]);
		}
	};

	self.open_uploader = function () {
		$("div#uploader_div").show();
		self.vue.is_uploading = true;
	};

	self.close_uploader = function () {
		$("div#uploader_div").hide();
		self.vue.is_uploading = false;
		$("input#file_input").val(""); // This clears the file choice once uploaded.

	};

	self.upload_file = function () {
		// Reads the file.
		var input = $('#file_input')[0];
		var file = input.files[0];
		if (file) {
			// First, gets an upload URL.
			console.log("Trying to get the upload url");
			$.getJSON('https://upload-dot-luca-teaching.appspot.com/start/uploader/get_upload_url',
				function (data) {
					// We now have upload (and download) URLs.
					var put_url = data['signed_url'];
					var get_url = data['access_url'];
					console.log("Received upload url: " + put_url);
					// Uploads the file, using the low-level interface.
					var req = new XMLHttpRequest();
					//req.addEventListener("load", self.upload_complete(get_url));
					//self.close_uploader();
					req.onreadystatechange = function () {
						if (this.readyState == 4 && this.status == 200) {
							console.log(this.responseText);
							self.upload_complete(get_url);
						}
					};
					// TODO: if you like, add a listener
					req.open("PUT", put_url, true);
					req.send(file);
				});
		}
	};


	self.upload_complete = function (get_url) {
		// Hides the uploader div.
		self.close_uploader();
		console.log('The file was uploaded; it is now available at ' + get_url);
		// TODO: The file is uploaded.  Now you have to insert the get_url into the database, etc.
		self.add_image(get_url);
	};

	self.get_userlist = function (firstrun) {
		var url = get_userlist;
		$.getJSON(url, function (data) {
			self.extend(self.vue.user_list, data.user_list);
			if (firstrun) self.get_user_images(self.vue.user.id, true);
		});
	}
	self.get_user_images = function (userid, ismyself) {
		self.vue.curid = userid;
		console.log(self.vue.curid);
		var url = get_user_images;
		$.getJSON(url + '/' + userid, function (data) {
			self.vue.user_images = data.user_images;
			self.vue.self_page = ismyself;
		});
	}
	self.add_image = function (imageurl) {
		if (!self.vue.user) {
			alert('please login to add');
			return;
		}
		$.ajax({
			type: "post",
			url: add_image,
			data: {
				imageurl: imageurl,
				price: self.vue.price
			},
			dataType: 'json',
			crossDomain: !0
		}).then(function (b) {
			//alert(b.msg);
			if (b.result) {
				//self.vue.user_images = b.user_images;
				if (b.user_images.length > 0)
					self.vue.user_images.splice(0, 0, b.user_images[0]);
			};
		}, function (a) {
			alert('network error');
		});
	}

	self.set_price = function (id) {
		if (!self.vue.user) {
			alert('please login to edit');
			return;
		}
		var obj = self.vue.user_images.find((n) => n.id == id);
		$.ajax({
			type: "post",
			url: set_price + '/' + obj.id,
			data: {
				price: obj.price,
				id: obj.id
			},
			dataType: 'json',
			crossDomain: !0
		}).then(function (b) {
			//alert(b.msg);
			if (b.result) {
				self.vue.user_images.splice(self.vue.user_images.indexOf(obj), 1, b.obj);
			};
		}, function (a) {
			alert('network error');
		});
	}

	self.get_user = function () {
		$.getJSON(user_url, function (data) {
			if (data) {
				self.vue.user = data;
				self.vue.curid = data.id;
				self.get_userlist(true);
			} else {
				self.vue.user = null;
				self.vue.curid = null;
			}

		});
	}
	self.change_cart = function (id) {
		var obj = self.vue.user_images.find((n) => n.id == id);
		if (self.vue.cart.indexOf(id) == -1) {
			self.vue.cart.push(id);
			self.vue.cart_images.push(obj);
			self.vue.cart_total += obj.price;
		} else {
			self.vue.cart.pop(id);
			self.vue.cart_images.pop(obj);
			self.vue.cart_total -= obj.price;
		}
	}
	self.checkout = function () {
		self.vue.is_checkout = true;
		self.stripe_instance = StripeCheckout.configure({
			key: 'pk_test_gTKHsvMrhWiU3SbTLDOHWFQ7', //put your own publishable key here
			image: 'https://stripe.com/img/documentation/checkout/marketplace.png',
			locale: 'auto',
			token: function (token, args) {
				console.log('got a token. sending data to localhost.');
				self.stripe_token = token;
				self.customer_info = args;
				self.send_data_to_server();
			}
		});
	}
	self.goback = function () {
		self.vue.is_checkout = false;
	}
	self.pay = function () {

		self.stripe_instance.open({
			name: "Your nice cart",
			description: "Buy cart content",
			billingAddress: true,
			shippingAddress: true,
			amount: Math.round(self.vue.cart_total * 100),
		});
	}
	self.send_data_to_server = function () {
		console.log("Payment for:", self.customer_info);
		// Calls the server.
		$.post(purchase_url, {
				customer_info: JSON.stringify(self.customer_info),
				transaction_token: JSON.stringify(self.stripe_token),
				amount: self.vue.cart_total,
				cart: JSON.stringify(self.vue.cart_images),
			},
			function (data) {
				// The order was successful.
				self.vue.cart = [];
				self.vue.cart_images = [];
				self.vue.cart_total = 0;
				self.vue.is_checkout = false;
				alert("Thank you for your purchase");
			}
		);
	};

	// Complete as needed.
	self.vue = new Vue({
		el: "#vue-div",
		delimiters: ['${', '}'],
		unsafeDelimiters: ['!{', '}'],
		data: {
			user_list: [],
			user_images: [],
			user: {},
			curid: undefined,
			price: undefined,
			cart: [],
			cart_images: [],
			cart_total: 0,
			is_checkout: false,
			is_uploading: false,
			self_page: true // Leave it to true, so initially you are looking at your own images.
		},
		methods: {
			get_user: self.get_user,
			get_userlist: self.get_userlist,
			add_image: self.add_image,
			get_user_images: self.get_user_images,
			open_uploader: self.open_uploader,
			close_uploader: self.close_uploader,
			upload_file: self.upload_file,
			set_price: self.set_price,
			change_cart: self.change_cart,
			checkout: self.checkout,
			pay: self.pay,
			goback: self.goback
		}
	});

	self.get_user();

	$('#vue-div').show();

	return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function () {
	APP = app();
});
