CREATE DATABASE FAQ_Project;
USE FAQ_Project;

CREATE DATABASE IF NOT EXISTS FAQ_Project;
USE FAQ_Project;

CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE
);

-- Step 3: Create the faqs table with foreign key to categories
CREATE TABLE IF NOT EXISTS faqs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Step 4: Insert categories
INSERT INTO categories (name) VALUES 
('Returns'),
('Retail'),
('Website'),
('App'),
('Orders'),
('Shipping'),
('Payments');

-- Step 5: Insert FAQs with category_id references
INSERT INTO faqs (category_id, question, answer) VALUES
(1, 'What is your return policy?', 'You can return items within 30 days of purchase.'),
(1, 'Are returns free?', 'Yes, return shipping is free for all orders.'),
(1, 'Can I return an item without the receipt?', 'A receipt or proof of purchase is required.'),
(1, 'How long does it take to get a refund?', 'Refunds are processed within 5-7 business days.'),
(1, 'Can I return items bought on sale?', 'Sale items can be returned unless marked final sale.'),

(2, 'Where are your physical stores located?', 'Our store locator is available on the website.'),
(2, 'Do you offer in-store pickup?', 'Yes, select ''Pickup In-Store'' during checkout.'),
(2, 'What are your store hours?', 'Most stores operate from 10 AM to 9 PM.'),
(2, 'Is parking available at stores?', 'Yes, all locations have customer parking.'),
(2, 'Can I check in-store availability online?', 'Yes, select a store and check stock on the product page.'),

(3, 'I''m facing issues logging in.', 'Try resetting your password or contact support.'),
(3, 'How do I track my order?', 'Log in and go to ''My Orders'' to track.'),
(3, 'I’m not receiving confirmation emails.', 'Check your spam folder and whitelist our email.'),
(3, 'Is my personal information secure?', 'Yes, we use encryption to protect your data.'),
(3, 'Can I save items for later?', 'Yes, use the wishlist feature.'),

(4, 'Is the app available for iOS and Android?', 'Yes, it''s available on both platforms.'),
(4, 'How do I update the app?', 'Visit the App Store or Play Store to update.'),
(4, 'The app is crashing frequently.', 'Try reinstalling or updating the app.'),
(4, 'Can I use coupons in the app?', 'Yes, enter them at checkout.'),
(4, 'How do I turn on notifications?', 'Enable them via Settings > Notifications.'),

(5, 'How do I cancel an order?', 'Go to ''My Orders'' and click ''Cancel'' next to the item.'),
(5, 'Can I modify my order after placing it?', 'You can only cancel and reorder; modifications aren''t supported.'),
(5, 'I received the wrong item.', 'Contact support and we’ll arrange a replacement.'),
(5, 'Do you ship internationally?', 'Currently, we only ship within the country.'),
(5, 'What if my order arrives damaged?', 'Contact support with a photo for assistance.'),

(6, 'What are your shipping options?', 'We offer Standard, Express, and Overnight shipping.'),
(6, 'How can I track my shipment?', 'Tracking info is emailed and available under ''My Orders''.'),
(6, 'Do you offer free shipping?', 'Yes, for orders over ₹999.'),
(6, 'Can I change the delivery address?', 'Only before dispatch. Contact support ASAP.'),
(6, 'What if my package is lost?', 'We''ll investigate and either resend or refund.'),

(7, 'What payment methods do you accept?', 'We accept UPI, credit/debit cards, and wallets.'),
(7, 'Is Cash on Delivery available?', 'Yes, COD is available on orders below ₹5,000.'),
(7, 'I was charged twice.', 'Contact support with transaction details.'),
(7, 'Can I get an invoice?', 'Invoices are emailed and also available in your account.'),
(7, 'Is EMI available?', 'EMI options are available for select cards during checkout.');


SELECT * FROM FAQS;
SELECT * FROM categories;