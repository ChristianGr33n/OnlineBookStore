-- This file is solely for inserting data into the database for testing purposes

INSERT INTO store  OVERRIDING SYSTEM VALUE VALUES (1, 0);
INSERT INTO publisher VALUES ('bloomsbury', '124535', 'b@g.ca');
INSERT INTO publisher VALUES ('viking', '54321', 'v@g.ca');
INSERT INTO publisher VALUES ('lioncrest', '67890', 'l@g.ca');
INSERT INTO book OVERRIDING SYSTEM VALUE VALUES (1, 10, 0.80, 100, 'bloomsbury', 'potter');
INSERT INTO book OVERRIDING SYSTEM VALUE VALUES (2, 15, 0.67, 150, 'bloomsbury', 'little prince');
INSERT INTO book OVERRIDING SYSTEM VALUE VALUES (3, 20, 0.89, 223, 'bloomsbury', 'potter 2');
INSERT INTO book OVERRIDING SYSTEM VALUE VALUES (4, 21, 0.91, 352, 'viking', 'it');
INSERT INTO book OVERRIDING SYSTEM VALUE VALUES (5, 34, 0.91, 324, 'viking', 'misery');
INSERT INTO book OVERRIDING SYSTEM VALUE VALUES (6, 8, 0.53, 342, 'lioncrest', 'cant hurt me');

INSERT INTO genre VALUES (1, 'fantasy');
INSERT INTO genre VALUES (2, 'adventure');
INSERT INTO genre VALUES (2, 'fantasy');
INSERT INTO genre VALUES (2, 'fable');
INSERT INTO genre VALUES (3, 'fantasy');
INSERT INTO genre VALUES (3, 'adventure');
INSERT INTO genre VALUES (3, 'action');
INSERT INTO genre VALUES (4, 'horror');
INSERT INTO genre VALUES (5, 'horror');
INSERT INTO genre VALUES (5, 'inspiration');
INSERT INTO genre VALUES (5, 'adventure');
INSERT INTO genre VALUES (5, 'action');


INSERT INTO author VALUES (1, 'JK');
INSERT INTO author VALUES (1, 'Joe');
INSERT INTO author VALUES (2, 'Antoine');
INSERT INTO author VALUES (3, 'JK');
INSERT INTO author VALUES (4, 'king');
INSERT INTO author VALUES (5, 'king');

INSERT INTO store_book VALUES (1, 3, 6, 1);
INSERT INTO store_book VALUES (2, 1, 8, 1);
INSERT INTO store_book VALUES (5, 1, 5, 1);


-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;