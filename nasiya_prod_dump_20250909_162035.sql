--
-- PostgreSQL database dump
--

\restrict 67zMrtMaPVOodK8KJTcPeXUXxnzn15x2x1IsNe0IoXM3OOicEPGVbY4v08ejncC

-- Dumped from database version 14.19 (Ubuntu 14.19-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.19 (Ubuntu 14.19-0ubuntu0.22.04.1)

-- Started on 2025-09-09 16:20:36 +05

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_manager_id_fkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_magazine_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transactions DROP CONSTRAINT IF EXISTS transactions_seller_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transactions DROP CONSTRAINT IF EXISTS transactions_sale_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transactions DROP CONSTRAINT IF EXISTS transactions_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transactions DROP CONSTRAINT IF EXISTS transactions_magazine_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transactions DROP CONSTRAINT IF EXISTS transactions_loan_payment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transactions DROP CONSTRAINT IF EXISTS transactions_loan_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transactions DROP CONSTRAINT IF EXISTS transactions_client_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales DROP CONSTRAINT IF EXISTS sales_seller_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales DROP CONSTRAINT IF EXISTS sales_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales DROP CONSTRAINT IF EXISTS sales_magazine_id_fkey;
ALTER TABLE IF EXISTS ONLY public.push_tokens DROP CONSTRAINT IF EXISTS push_tokens_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_manager_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_sender_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_recipient_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_push_token_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notification_preferences DROP CONSTRAINT IF EXISTS notification_preferences_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.magazines DROP CONSTRAINT IF EXISTS magazines_approved_by_fkey;
ALTER TABLE IF EXISTS ONLY public.loans DROP CONSTRAINT IF EXISTS loans_seller_id_fkey;
ALTER TABLE IF EXISTS ONLY public.loans DROP CONSTRAINT IF EXISTS loans_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.loans DROP CONSTRAINT IF EXISTS loans_magazine_id_fkey;
ALTER TABLE IF EXISTS ONLY public.loans DROP CONSTRAINT IF EXISTS loans_client_id_fkey;
ALTER TABLE IF EXISTS ONLY public.loan_payments DROP CONSTRAINT IF EXISTS loan_payments_loan_id_fkey;
ALTER TABLE IF EXISTS ONLY public.clients DROP CONSTRAINT IF EXISTS clients_manager_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_sales DROP CONSTRAINT IF EXISTS auto_sales_seller_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_sales DROP CONSTRAINT IF EXISTS auto_sales_magazine_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_sales DROP CONSTRAINT IF EXISTS auto_sales_auto_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_products DROP CONSTRAINT IF EXISTS auto_products_manager_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_loans DROP CONSTRAINT IF EXISTS auto_loans_seller_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_loans DROP CONSTRAINT IF EXISTS auto_loans_magazine_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_loans DROP CONSTRAINT IF EXISTS auto_loans_client_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_loans DROP CONSTRAINT IF EXISTS auto_loans_auto_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.auto_loan_payments DROP CONSTRAINT IF EXISTS auto_loan_payments_auto_loan_id_fkey;
DROP INDEX IF EXISTS public.ix_users_phone;
DROP INDEX IF EXISTS public.ix_users_id;
DROP INDEX IF EXISTS public.ix_transactions_id;
DROP INDEX IF EXISTS public.ix_sales_id;
DROP INDEX IF EXISTS public.ix_push_tokens_token;
DROP INDEX IF EXISTS public.ix_push_tokens_id;
DROP INDEX IF EXISTS public.ix_products_name;
DROP INDEX IF EXISTS public.ix_products_id;
DROP INDEX IF EXISTS public.ix_notifications_id;
DROP INDEX IF EXISTS public.ix_notification_preferences_id;
DROP INDEX IF EXISTS public.ix_magazines_name;
DROP INDEX IF EXISTS public.ix_magazines_id;
DROP INDEX IF EXISTS public.ix_loans_id;
DROP INDEX IF EXISTS public.ix_loan_payments_id;
DROP INDEX IF EXISTS public.ix_clients_passport_series;
DROP INDEX IF EXISTS public.ix_clients_id;
DROP INDEX IF EXISTS public.idx_sales_imei;
DROP INDEX IF EXISTS public.idx_loans_imei;
DROP INDEX IF EXISTS public.idx_auto_sales_seller_id;
DROP INDEX IF EXISTS public.idx_auto_sales_sale_date;
DROP INDEX IF EXISTS public.idx_auto_sales_auto_product_id;
DROP INDEX IF EXISTS public.idx_auto_products_manager_id;
DROP INDEX IF EXISTS public.idx_auto_products_car_name;
DROP INDEX IF EXISTS public.idx_auto_loans_seller_id;
DROP INDEX IF EXISTS public.idx_auto_loans_loan_start_date;
DROP INDEX IF EXISTS public.idx_auto_loans_client_id;
DROP INDEX IF EXISTS public.idx_auto_loans_auto_product_id;
DROP INDEX IF EXISTS public.idx_auto_loan_payments_status;
DROP INDEX IF EXISTS public.idx_auto_loan_payments_due_date;
DROP INDEX IF EXISTS public.idx_auto_loan_payments_auto_loan_id;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.push_tokens DROP CONSTRAINT IF EXISTS uq_user_token;
ALTER TABLE IF EXISTS ONLY public.transactions DROP CONSTRAINT IF EXISTS transactions_pkey;
ALTER TABLE IF EXISTS ONLY public.sales DROP CONSTRAINT IF EXISTS sales_pkey;
ALTER TABLE IF EXISTS ONLY public.push_tokens DROP CONSTRAINT IF EXISTS push_tokens_pkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_pkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_pkey;
ALTER TABLE IF EXISTS ONLY public.notification_preferences DROP CONSTRAINT IF EXISTS notification_preferences_pkey;
ALTER TABLE IF EXISTS ONLY public.magazines DROP CONSTRAINT IF EXISTS magazines_pkey;
ALTER TABLE IF EXISTS ONLY public.loans DROP CONSTRAINT IF EXISTS loans_pkey;
ALTER TABLE IF EXISTS ONLY public.loan_payments DROP CONSTRAINT IF EXISTS loan_payments_pkey;
ALTER TABLE IF EXISTS ONLY public.clients DROP CONSTRAINT IF EXISTS clients_pkey;
ALTER TABLE IF EXISTS ONLY public.auto_sales DROP CONSTRAINT IF EXISTS auto_sales_pkey;
ALTER TABLE IF EXISTS ONLY public.auto_products DROP CONSTRAINT IF EXISTS auto_products_pkey;
ALTER TABLE IF EXISTS ONLY public.auto_loans DROP CONSTRAINT IF EXISTS auto_loans_pkey;
ALTER TABLE IF EXISTS ONLY public.auto_loan_payments DROP CONSTRAINT IF EXISTS auto_loan_payments_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.transactions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.sales ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.push_tokens ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.products ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.notifications ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.notification_preferences ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.magazines ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.loans ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.loan_payments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.clients ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auto_sales ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auto_products ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auto_loans ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auto_loan_payments ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.transactions_id_seq;
DROP TABLE IF EXISTS public.transactions;
DROP SEQUENCE IF EXISTS public.sales_id_seq;
DROP TABLE IF EXISTS public.sales;
DROP SEQUENCE IF EXISTS public.push_tokens_id_seq;
DROP TABLE IF EXISTS public.push_tokens;
DROP SEQUENCE IF EXISTS public.products_id_seq;
DROP TABLE IF EXISTS public.products;
DROP SEQUENCE IF EXISTS public.notifications_id_seq;
DROP TABLE IF EXISTS public.notifications;
DROP SEQUENCE IF EXISTS public.notification_preferences_id_seq;
DROP TABLE IF EXISTS public.notification_preferences;
DROP SEQUENCE IF EXISTS public.magazines_id_seq;
DROP TABLE IF EXISTS public.magazines;
DROP SEQUENCE IF EXISTS public.loans_id_seq;
DROP TABLE IF EXISTS public.loans;
DROP SEQUENCE IF EXISTS public.loan_payments_id_seq;
DROP TABLE IF EXISTS public.loan_payments;
DROP SEQUENCE IF EXISTS public.clients_id_seq;
DROP TABLE IF EXISTS public.clients;
DROP SEQUENCE IF EXISTS public.auto_sales_id_seq;
DROP TABLE IF EXISTS public.auto_sales;
DROP SEQUENCE IF EXISTS public.auto_products_id_seq;
DROP TABLE IF EXISTS public.auto_products;
DROP SEQUENCE IF EXISTS public.auto_loans_id_seq;
DROP TABLE IF EXISTS public.auto_loans;
DROP SEQUENCE IF EXISTS public.auto_loan_payments_id_seq;
DROP TABLE IF EXISTS public.auto_loan_payments;
DROP TYPE IF EXISTS public.usertype;
DROP TYPE IF EXISTS public.userstatus;
DROP TYPE IF EXISTS public.userrole;
DROP TYPE IF EXISTS public.transactiontype;
DROP TYPE IF EXISTS public.paymentstatus;
DROP TYPE IF EXISTS public.notificationtype;
DROP TYPE IF EXISTS public.notificationstatus;
DROP TYPE IF EXISTS public.magazinestatus;
DROP TYPE IF EXISTS public.devicetype;
--
-- TOC entry 890 (class 1247 OID 16668)
-- Name: devicetype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.devicetype AS ENUM (
    'mobile',
    'web'
);


--
-- TOC entry 851 (class 1247 OID 16387)
-- Name: magazinestatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.magazinestatus AS ENUM (
    'PENDING',
    'ACTIVE',
    'INACTIVE'
);


--
-- TOC entry 896 (class 1247 OID 16690)
-- Name: notificationstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.notificationstatus AS ENUM (
    'pending',
    'sent',
    'failed',
    'delivered'
);


--
-- TOC entry 893 (class 1247 OID 16676)
-- Name: notificationtype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.notificationtype AS ENUM (
    'new_user_registration',
    'payment_overdue',
    'loan_approved',
    'loan_rejected',
    'payment_reminder'
);


--
-- TOC entry 860 (class 1247 OID 16410)
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.paymentstatus AS ENUM (
    'PENDING',
    'PAID',
    'OVERDUE'
);


--
-- TOC entry 863 (class 1247 OID 16418)
-- Name: transactiontype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.transactiontype AS ENUM (
    'SALE',
    'LOAN',
    'LOAN_PAYMENT',
    'PRODUCT_RESTOCK',
    'REFUND'
);


--
-- TOC entry 854 (class 1247 OID 16394)
-- Name: userrole; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'MANAGER',
    'SELLER'
);


--
-- TOC entry 857 (class 1247 OID 16402)
-- Name: userstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.userstatus AS ENUM (
    'PENDING',
    'ACTIVE',
    'INACTIVE'
);


--
-- TOC entry 908 (class 1247 OID 16931)
-- Name: usertype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.usertype AS ENUM (
    'gadgets',
    'auto'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 238 (class 1259 OID 17089)
-- Name: auto_loan_payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auto_loan_payments (
    id integer NOT NULL,
    amount double precision NOT NULL,
    payment_date timestamp with time zone,
    due_date timestamp with time zone NOT NULL,
    status public.paymentstatus DEFAULT 'PENDING'::public.paymentstatus,
    is_late boolean DEFAULT false,
    is_full_payment boolean DEFAULT false,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    auto_loan_id integer NOT NULL
);


--
-- TOC entry 237 (class 1259 OID 17088)
-- Name: auto_loan_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auto_loan_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3569 (class 0 OID 0)
-- Dependencies: 237
-- Name: auto_loan_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auto_loan_payments_id_seq OWNED BY public.auto_loan_payments.id;


--
-- TOC entry 236 (class 1259 OID 17058)
-- Name: auto_loans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auto_loans (
    id integer NOT NULL,
    loan_price double precision NOT NULL,
    initial_payment double precision NOT NULL,
    remaining_amount double precision NOT NULL,
    loan_months integer NOT NULL,
    yearly_interest_rate double precision NOT NULL,
    monthly_payment double precision NOT NULL,
    loan_start_date timestamp with time zone NOT NULL,
    video_url character varying,
    agreement_images text,
    is_completed boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    auto_product_id integer NOT NULL,
    client_id integer NOT NULL,
    seller_id integer NOT NULL,
    magazine_id integer NOT NULL
);


--
-- TOC entry 235 (class 1259 OID 17057)
-- Name: auto_loans_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auto_loans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3570 (class 0 OID 0)
-- Dependencies: 235
-- Name: auto_loans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auto_loans_id_seq OWNED BY public.auto_loans.id;


--
-- TOC entry 232 (class 1259 OID 17016)
-- Name: auto_products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auto_products (
    id integer NOT NULL,
    car_name character varying NOT NULL,
    model character varying NOT NULL,
    color character varying NOT NULL,
    year integer NOT NULL,
    purchase_price double precision NOT NULL,
    sale_price double precision NOT NULL,
    count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    manager_id integer NOT NULL
);


--
-- TOC entry 231 (class 1259 OID 17015)
-- Name: auto_products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auto_products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3571 (class 0 OID 0)
-- Dependencies: 231
-- Name: auto_products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auto_products_id_seq OWNED BY public.auto_products.id;


--
-- TOC entry 234 (class 1259 OID 17034)
-- Name: auto_sales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auto_sales (
    id integer NOT NULL,
    sale_price double precision NOT NULL,
    sale_date timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    auto_product_id integer NOT NULL,
    seller_id integer NOT NULL,
    magazine_id integer NOT NULL
);


--
-- TOC entry 233 (class 1259 OID 17033)
-- Name: auto_sales_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auto_sales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3572 (class 0 OID 0)
-- Dependencies: 233
-- Name: auto_sales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auto_sales_id_seq OWNED BY public.auto_sales.id;


--
-- TOC entry 214 (class 1259 OID 16454)
-- Name: clients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clients (
    id integer NOT NULL,
    name character varying NOT NULL,
    phone character varying NOT NULL,
    passport_series character varying NOT NULL,
    passport_image_url character varying,
    passport_image_urls character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    manager_id integer NOT NULL
);


--
-- TOC entry 213 (class 1259 OID 16453)
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3573 (class 0 OID 0)
-- Dependencies: 213
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- TOC entry 222 (class 1259 OID 16541)
-- Name: loan_payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.loan_payments (
    id integer NOT NULL,
    amount double precision NOT NULL,
    payment_date timestamp with time zone,
    due_date timestamp with time zone NOT NULL,
    status public.paymentstatus,
    is_late boolean,
    is_full_payment boolean,
    notes text,
    created_at timestamp with time zone,
    loan_id integer NOT NULL
);


--
-- TOC entry 221 (class 1259 OID 16540)
-- Name: loan_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.loan_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3574 (class 0 OID 0)
-- Dependencies: 221
-- Name: loan_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.loan_payments_id_seq OWNED BY public.loan_payments.id;


--
-- TOC entry 220 (class 1259 OID 16511)
-- Name: loans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.loans (
    id integer NOT NULL,
    loan_price double precision NOT NULL,
    initial_payment double precision NOT NULL,
    remaining_amount double precision NOT NULL,
    loan_months integer NOT NULL,
    interest_rate double precision NOT NULL,
    monthly_payment double precision NOT NULL,
    loan_start_date timestamp with time zone NOT NULL,
    video_url character varying,
    agreement_images text,
    is_completed boolean,
    created_at timestamp with time zone,
    product_id integer NOT NULL,
    client_id integer NOT NULL,
    seller_id integer NOT NULL,
    magazine_id integer NOT NULL,
    imei character varying(20)
);


--
-- TOC entry 219 (class 1259 OID 16510)
-- Name: loans_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.loans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3575 (class 0 OID 0)
-- Dependencies: 219
-- Name: loans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.loans_id_seq OWNED BY public.loans.id;


--
-- TOC entry 210 (class 1259 OID 16430)
-- Name: magazines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.magazines (
    id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    address character varying,
    phone character varying,
    status public.magazinestatus,
    subscription_end_date date,
    approved_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- TOC entry 209 (class 1259 OID 16429)
-- Name: magazines_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.magazines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3576 (class 0 OID 0)
-- Dependencies: 209
-- Name: magazines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.magazines_id_seq OWNED BY public.magazines.id;


--
-- TOC entry 228 (class 1259 OID 16717)
-- Name: notification_preferences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notification_preferences (
    id integer NOT NULL,
    user_id integer NOT NULL,
    notification_type public.notificationtype NOT NULL,
    is_enabled boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- TOC entry 227 (class 1259 OID 16716)
-- Name: notification_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notification_preferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3577 (class 0 OID 0)
-- Dependencies: 227
-- Name: notification_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notification_preferences_id_seq OWNED BY public.notification_preferences.id;


--
-- TOC entry 230 (class 1259 OID 16731)
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    type public.notificationtype NOT NULL,
    title character varying NOT NULL,
    body text NOT NULL,
    data json,
    recipient_user_id integer,
    recipient_role character varying,
    sender_user_id integer,
    push_token_id integer,
    status public.notificationstatus,
    sent_at timestamp with time zone,
    delivered_at timestamp with time zone,
    error_message text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- TOC entry 229 (class 1259 OID 16730)
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3578 (class 0 OID 0)
-- Dependencies: 229
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- TOC entry 216 (class 1259 OID 16471)
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying NOT NULL,
    model character varying NOT NULL,
    price double precision NOT NULL,
    purchase_price double precision,
    sale_price double precision,
    count integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    manager_id integer NOT NULL
);


--
-- TOC entry 215 (class 1259 OID 16470)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3579 (class 0 OID 0)
-- Dependencies: 215
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 226 (class 1259 OID 16700)
-- Name: push_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.push_tokens (
    id integer NOT NULL,
    token character varying NOT NULL,
    user_id integer NOT NULL,
    device_type public.devicetype,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- TOC entry 225 (class 1259 OID 16699)
-- Name: push_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.push_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3580 (class 0 OID 0)
-- Dependencies: 225
-- Name: push_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.push_tokens_id_seq OWNED BY public.push_tokens.id;


--
-- TOC entry 218 (class 1259 OID 16488)
-- Name: sales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sales (
    id integer NOT NULL,
    sale_price double precision NOT NULL,
    sale_date timestamp with time zone,
    created_at timestamp with time zone,
    product_id integer NOT NULL,
    seller_id integer NOT NULL,
    magazine_id integer NOT NULL,
    imei character varying(20)
);


--
-- TOC entry 217 (class 1259 OID 16487)
-- Name: sales_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3581 (class 0 OID 0)
-- Dependencies: 217
-- Name: sales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sales_id_seq OWNED BY public.sales.id;


--
-- TOC entry 224 (class 1259 OID 16556)
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    type public.transactiontype NOT NULL,
    amount double precision NOT NULL,
    description text NOT NULL,
    created_at timestamp with time zone,
    sale_id integer,
    loan_id integer,
    loan_payment_id integer,
    product_id integer,
    client_id integer,
    seller_id integer NOT NULL,
    magazine_id integer NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 16555)
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3582 (class 0 OID 0)
-- Dependencies: 223
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- TOC entry 212 (class 1259 OID 16442)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying NOT NULL,
    phone character varying NOT NULL,
    password_hash character varying NOT NULL,
    role public.userrole NOT NULL,
    status public.userstatus,
    magazine_name character varying,
    subscription_end_date date,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    magazine_id integer,
    manager_id integer,
    user_type public.usertype DEFAULT 'gadgets'::public.usertype
);


--
-- TOC entry 211 (class 1259 OID 16441)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3583 (class 0 OID 0)
-- Dependencies: 211
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 3294 (class 2604 OID 17092)
-- Name: auto_loan_payments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loan_payments ALTER COLUMN id SET DEFAULT nextval('public.auto_loan_payments_id_seq'::regclass);


--
-- TOC entry 3291 (class 2604 OID 17061)
-- Name: auto_loans id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loans ALTER COLUMN id SET DEFAULT nextval('public.auto_loans_id_seq'::regclass);


--
-- TOC entry 3285 (class 2604 OID 17019)
-- Name: auto_products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_products ALTER COLUMN id SET DEFAULT nextval('public.auto_products_id_seq'::regclass);


--
-- TOC entry 3288 (class 2604 OID 17037)
-- Name: auto_sales id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_sales ALTER COLUMN id SET DEFAULT nextval('public.auto_sales_id_seq'::regclass);


--
-- TOC entry 3271 (class 2604 OID 16457)
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- TOC entry 3277 (class 2604 OID 16544)
-- Name: loan_payments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loan_payments ALTER COLUMN id SET DEFAULT nextval('public.loan_payments_id_seq'::regclass);


--
-- TOC entry 3276 (class 2604 OID 16514)
-- Name: loans id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loans ALTER COLUMN id SET DEFAULT nextval('public.loans_id_seq'::regclass);


--
-- TOC entry 3266 (class 2604 OID 16433)
-- Name: magazines id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.magazines ALTER COLUMN id SET DEFAULT nextval('public.magazines_id_seq'::regclass);


--
-- TOC entry 3281 (class 2604 OID 16720)
-- Name: notification_preferences id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification_preferences ALTER COLUMN id SET DEFAULT nextval('public.notification_preferences_id_seq'::regclass);


--
-- TOC entry 3283 (class 2604 OID 16734)
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- TOC entry 3273 (class 2604 OID 16474)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 3279 (class 2604 OID 16703)
-- Name: push_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_tokens ALTER COLUMN id SET DEFAULT nextval('public.push_tokens_id_seq'::regclass);


--
-- TOC entry 3275 (class 2604 OID 16491)
-- Name: sales id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales ALTER COLUMN id SET DEFAULT nextval('public.sales_id_seq'::regclass);


--
-- TOC entry 3278 (class 2604 OID 16559)
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- TOC entry 3268 (class 2604 OID 16445)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 3563 (class 0 OID 17089)
-- Dependencies: 238
-- Data for Name: auto_loan_payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auto_loan_payments (id, amount, payment_date, due_date, status, is_late, is_full_payment, notes, created_at, auto_loan_id) FROM stdin;
\.


--
-- TOC entry 3561 (class 0 OID 17058)
-- Dependencies: 236
-- Data for Name: auto_loans; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auto_loans (id, loan_price, initial_payment, remaining_amount, loan_months, yearly_interest_rate, monthly_payment, loan_start_date, video_url, agreement_images, is_completed, created_at, auto_product_id, client_id, seller_id, magazine_id) FROM stdin;
\.


--
-- TOC entry 3557 (class 0 OID 17016)
-- Dependencies: 232
-- Data for Name: auto_products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auto_products (id, car_name, model, color, year, purchase_price, sale_price, count, created_at, updated_at, manager_id) FROM stdin;
\.


--
-- TOC entry 3559 (class 0 OID 17034)
-- Dependencies: 234
-- Data for Name: auto_sales; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auto_sales (id, sale_price, sale_date, created_at, auto_product_id, seller_id, magazine_id) FROM stdin;
\.


--
-- TOC entry 3539 (class 0 OID 16454)
-- Dependencies: 214
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.clients (id, name, phone, passport_series, passport_image_url, passport_image_urls, created_at, updated_at, manager_id) FROM stdin;
1	Azim	+998994090129	AB12345	\N	\N	2025-08-03 05:07:31+05	\N	2
2	Shaxzod	+998931161613	AV12456	passports/3339a945-cc76-4f93-bc02-befb4ccd182a.png	\N	2025-08-03 06:46:36+05	\N	2
3	Abdurahmon	+998988808086	AB3344888	passports/08b5f7e8-2f22-4106-b901-74335ed12d29.jpeg	\N	2025-08-03 15:51:35+05	\N	4
4	Shaxzod	+998931161613	AV13552	passports/78fb8188-6bbd-44f4-8e04-4659e0c301cb.png	\N	2025-08-03 16:05:41+05	\N	5
5	Giyos	+998906541237	AC1245	passports/c5d4ad7b-b22c-48b2-a3a9-fef99db210f6.png	\N	2025-08-03 16:24:30+05	\N	2
6	Nodir	+998991234567	AB213567	passports/dd4d36fb-b48d-4db5-af1b-1b96943f47a2.png	\N	2025-08-09 18:16:28+05	\N	7
7	Muhammad Said 	+998940489840	AB7793526	passports/3d6dc61f-b49b-45e2-bb9c-1b72bd10daea.jpeg	\N	2025-08-17 10:44:54+05	\N	2
8	Abdumajid	+998987654321	AB213456	passports/08f980db-9909-4b2a-a0be-559b8b3fdfb5.jpg	["passports/08f980db-9909-4b2a-a0be-559b8b3fdfb5.jpg", "passports/84c101ca-84ec-453c-8bbf-89c3e768835b.jpg", "passports/08c4334c-7594-418e-8525-946df7ec2972.jpg"]	2025-08-18 19:10:25+05	\N	5
9	Abdurashid	+998957654321	AV098765	passports/ea355cce-26d4-4b78-a8b6-3edf3758b4b2.jpg	["passports/ea355cce-26d4-4b78-a8b6-3edf3758b4b2.jpg", "passports/d4138e14-bb24-4684-ab29-b99d54598d08.jpg", "passports/e82f5be6-bf34-4d23-a0ac-3117bb46f9c4.png"]	2025-08-18 19:26:33+05	\N	5
10	Abdulaziz	+998999999999	AV8622222	passports/bff9a2ef-5b88-4b00-baac-a15266bb99b2.jpeg	["passports/bff9a2ef-5b88-4b00-baac-a15266bb99b2.jpeg"]	2025-08-28 17:35:18+05	\N	21
11	Azizbek	+998770730624	AB12354	passports/da15b2c7-8671-4c1a-9986-33f99950f8fb.jpg	["passports/da15b2c7-8671-4c1a-9986-33f99950f8fb.jpg"]	2025-08-31 12:53:28+05	\N	2
12	Muhammad Umar	+998851234567	AV32176	passports/e65b08ec-299c-46b7-8de2-7300e137244f.jpg	["passports/e65b08ec-299c-46b7-8de2-7300e137244f.jpg"]	2025-08-31 18:33:53.252278+05	\N	2
\.


--
-- TOC entry 3547 (class 0 OID 16541)
-- Dependencies: 222
-- Data for Name: loan_payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.loan_payments (id, amount, payment_date, due_date, status, is_late, is_full_payment, notes, created_at, loan_id) FROM stdin;
1	72.5	2025-08-03 00:00:00+05	2025-09-02 00:00:00+05	PAID	f	f	\N	2025-08-03 11:29:03.379182+05	1
2	72.5	2025-08-03 00:00:00+05	2025-10-02 00:00:00+05	PAID	f	f	\N	2025-08-03 11:29:03.379187+05	1
6	90	2025-08-03 06:47:56.42+05	2025-09-02 00:00:00+05	PAID	f	f	\N	2025-08-03 11:47:04.204968+05	2
11	210	2025-08-03 00:00:00+05	2025-08-03 00:00:00+05	PAID	f	t	Full loan payment - loan completed in one payment	2025-08-03 11:48:27.923534+05	2
12	105	2025-08-03 00:00:00+05	2025-08-03 00:00:00+05	PAID	f	t	Full loan payment - loan completed in one payment	2025-08-03 12:07:58.68428+05	1
13	90	2025-08-06 17:16:48.877+05	2025-09-02 00:00:00+05	PAID	f	f	\N	2025-08-03 21:23:58.154141+05	3
18	130	2025-08-03 17:19:23.636+05	2025-09-02 00:00:00+05	PAID	f	f	\N	2025-08-03 22:13:29.630429+05	4
23	270	2025-08-03 00:00:00+05	2025-08-03 00:00:00+05	PAID	f	t	Full loan payment - loan completed in one payment	2025-08-03 22:20:32.426524+05	4
24	600	2025-08-03 18:24:25.927+05	2025-09-02 00:00:00+05	PAID	f	f	\N	2025-08-03 22:34:56.293742+05	5
25	100	\N	2025-10-02 00:00:00+05	PENDING	f	f	\N	2025-08-03 22:34:56.293747+05	5
26	100	\N	2025-11-01 00:00:00+05	PENDING	f	f	\N	2025-08-03 22:34:56.293748+05	5
27	100	\N	2025-12-01 00:00:00+05	PENDING	f	f	\N	2025-08-03 22:34:56.293749+05	5
28	100	\N	2025-12-31 00:00:00+05	PENDING	f	f	\N	2025-08-03 22:34:56.29375+05	5
29	100	\N	2026-01-30 00:00:00+05	PENDING	f	f	\N	2025-08-03 22:34:56.293751+05	5
30	140	2025-08-03 00:00:00+05	2025-09-02 00:00:00+05	PAID	f	f	\N	2025-08-03 23:26:44.126716+05	6
31	140	2025-08-04 00:00:00+05	2025-10-02 00:00:00+05	PAID	f	f	\N	2025-08-03 23:26:44.12672+05	6
32	140	\N	2025-11-01 00:00:00+05	PENDING	f	f	\N	2025-08-03 23:26:44.126721+05	6
33	100	2025-08-03 00:00:00+05	2025-09-02 00:00:00+05	PAID	f	f	\N	2025-08-04 01:19:43.918986+05	7
34	550	2025-08-03 20:21:24.593+05	2025-10-02 00:00:00+05	PAID	f	f	\N	2025-08-04 01:19:43.918991+05	7
35	100	2025-08-03 20:21:38.241+05	2025-11-01 00:00:00+05	PAID	f	f	\N	2025-08-04 01:19:43.918992+05	7
36	100	\N	2025-12-01 00:00:00+05	PENDING	f	f	\N	2025-08-04 01:19:43.918993+05	7
37	100	\N	2025-12-31 00:00:00+05	PENDING	f	f	\N	2025-08-04 01:19:43.918994+05	7
38	100	\N	2026-01-30 00:00:00+05	PENDING	f	f	\N	2025-08-04 01:19:43.918995+05	7
39	125	2025-08-04 00:00:00+05	2025-09-03 00:00:00+05	PAID	f	f	\N	2025-08-04 11:19:09.350407+05	8
45	625	2025-08-04 00:00:00+05	2025-08-04 00:00:00+05	PAID	f	t	Full loan payment - loan completed in one payment	2025-08-04 11:42:12.108776+05	8
52	500	2025-08-04 00:00:00+05	2025-08-04 00:00:00+05	PAID	f	t	Full loan payment - loan completed in one payment	2025-08-04 12:28:37.247664+05	9
59	520	2025-08-05 00:00:00+05	2025-08-05 00:00:00+05	PAID	f	t	Full loan payment - loan completed in one payment	2025-08-05 20:13:33.931832+05	10
60	186.67	\N	2025-09-05 00:00:00+05	PENDING	f	f	\N	2025-08-06 21:48:17.805726+05	11
61	186.67	\N	2025-10-05 00:00:00+05	PENDING	f	f	\N	2025-08-06 21:48:17.805731+05	11
62	186.67	\N	2025-11-04 00:00:00+05	PENDING	f	f	\N	2025-08-06 21:48:17.805732+05	11
63	168	2025-08-06 17:24:02.777+05	2025-09-05 00:00:00+05	PAID	f	f	\N	2025-08-06 22:19:25.327458+05	12
64	168	2025-08-28 00:00:00+05	2025-10-05 00:00:00+05	PAID	f	f	\N	2025-08-06 22:19:25.327465+05	12
65	168	2025-08-28 00:00:00+05	2025-11-04 00:00:00+05	PAID	f	f	\N	2025-08-06 22:19:25.327467+05	12
66	168	2025-08-28 00:00:00+05	2025-12-04 00:00:00+05	PAID	f	f	\N	2025-08-06 22:19:25.327468+05	12
67	168	\N	2026-01-03 00:00:00+05	PENDING	f	f	\N	2025-08-06 22:19:25.327471+05	12
73	125	\N	2025-09-08 00:00:00+05	PENDING	f	f	\N	2025-08-09 23:18:42.820941+05	14
74	125	\N	2025-10-08 00:00:00+05	PENDING	f	f	\N	2025-08-09 23:18:42.820946+05	14
75	125	\N	2025-11-07 00:00:00+05	PENDING	f	f	\N	2025-08-09 23:18:42.820947+05	14
76	700	2025-08-11 00:00:00+05	2025-08-11 00:00:00+05	PAID	f	t	Full loan payment - loan completed in one payment	2025-08-11 13:43:10.206986+05	13
77	60	2025-08-12 00:00:00+05	2025-09-11 00:00:00+05	PAID	f	f	\N	2025-08-12 12:28:32.851918+05	15
78	60	\N	2025-10-11 00:00:00+05	PENDING	f	f	\N	2025-08-12 12:28:32.851922+05	15
79	60	\N	2025-11-10 00:00:00+05	PENDING	f	f	\N	2025-08-12 12:28:32.851924+05	15
80	60	\N	2025-12-10 00:00:00+05	PENDING	f	f	\N	2025-08-12 12:28:32.851924+05	15
81	60	\N	2026-01-09 00:00:00+05	PENDING	f	f	\N	2025-08-12 12:28:32.851925+05	15
82	210	2025-08-17 00:00:00+05	2025-08-17 00:00:00+05	PAID	f	t	Full loan payment - loan completed in one payment	2025-08-17 15:51:28.942699+05	3
83	210	2025-08-28 00:00:00+05	2025-09-27 00:00:00+05	PAID	f	f	\N	2025-08-28 22:37:52.434991+05	16
84	150	2025-08-29 14:01:45.923+05	2025-10-27 00:00:00+05	PAID	f	f	\N	2025-08-28 22:37:52.434999+05	16
85	210	\N	2025-11-26 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:37:52.435001+05	16
86	210	\N	2025-12-26 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:37:52.435003+05	16
87	210	\N	2026-01-25 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:37:52.435005+05	16
88	210	\N	2026-02-24 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:37:52.435006+05	16
89	60	2025-08-28 17:58:47.76+05	2025-03-27 00:00:00+05	PAID	f	f	\N	2025-08-28 22:58:11.902455+05	17
90	80	2025-08-28 18:02:13.031+05	2025-04-26 00:00:00+05	PAID	f	f	\N	2025-08-28 22:58:11.90246+05	17
91	75	\N	2025-05-26 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:58:11.902462+05	17
92	75	\N	2025-06-25 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:58:11.902462+05	17
93	75	\N	2025-07-25 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:58:11.902463+05	17
94	75	\N	2025-08-24 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:58:11.902464+05	17
95	75	\N	2025-09-23 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:58:11.902465+05	17
96	75	\N	2025-10-23 00:00:00+05	PENDING	f	f	\N	2025-08-28 22:58:11.902466+05	17
100	165	\N	2025-09-28 00:00:00+05	PENDING	f	f	\N	2025-09-01 00:38:41.991103+05	18
101	165	\N	2025-10-28 00:00:00+05	PENDING	f	f	\N	2025-09-01 00:38:41.991104+05	18
102	165	\N	2025-11-27 00:00:00+05	PENDING	f	f	\N	2025-09-01 00:38:41.991105+05	18
103	165	\N	2025-12-27 00:00:00+05	PENDING	f	f	\N	2025-09-01 00:38:41.991106+05	18
104	165	\N	2026-01-26 00:00:00+05	PENDING	f	f	\N	2025-09-01 00:38:41.991107+05	18
105	165	\N	2026-02-25 00:00:00+05	PENDING	f	f	\N	2025-09-01 00:38:41.991108+05	18
106	165	\N	2026-03-27 00:00:00+05	PENDING	f	f	\N	2025-09-01 00:38:41.991109+05	18
97	165	2025-08-31 00:00:00+05	2025-06-30 00:00:00+05	PAID	f	f	\N	2025-09-01 00:38:41.991095+05	18
98	165	2025-09-01 00:00:00+05	2025-07-30 00:00:00+05	PAID	f	f	\N	2025-09-01 00:38:41.991101+05	18
99	165	2025-09-01 00:00:00+05	2025-08-29 00:00:00+05	PAID	f	f	\N	2025-09-01 00:38:41.991102+05	18
107	93.33	\N	2025-10-01 00:00:00+05	PENDING	f	f	\N	2025-09-01 15:09:58.246923+05	19
108	93.33	\N	2025-10-31 00:00:00+05	PENDING	f	f	\N	2025-09-01 15:09:58.246931+05	19
109	93.33	\N	2025-11-30 00:00:00+05	PENDING	f	f	\N	2025-09-01 15:09:58.246932+05	19
110	93.33	\N	2025-12-30 00:00:00+05	PENDING	f	f	\N	2025-09-01 15:09:58.246933+05	19
111	93.33	\N	2026-01-29 00:00:00+05	PENDING	f	f	\N	2025-09-01 15:09:58.246934+05	19
112	93.33	\N	2026-02-28 00:00:00+05	PENDING	f	f	\N	2025-09-01 15:09:58.246935+05	19
113	213.33	\N	2025-05-31 00:00:00+05	PENDING	f	f	\N	2025-09-01 17:02:14.145468+05	20
114	213.33	\N	2025-06-30 00:00:00+05	PENDING	f	f	\N	2025-09-01 17:02:14.145474+05	20
115	213.33	\N	2025-07-30 00:00:00+05	PENDING	f	f	\N	2025-09-01 17:02:14.145475+05	20
\.


--
-- TOC entry 3545 (class 0 OID 16511)
-- Dependencies: 220
-- Data for Name: loans; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.loans (id, loan_price, initial_payment, remaining_amount, loan_months, interest_rate, monthly_payment, loan_start_date, video_url, agreement_images, is_completed, created_at, product_id, client_id, seller_id, magazine_id, imei) FROM stdin;
1	300	50	0	5	45	72.5	2025-08-03 10:00:00+05	videos/58d45730-ba46-4ca1-8553-539be58f2413.mov	["agreements/ce6455f3-ce5e-4b58-9411-7ba4306e3092.jpg"]	t	2025-08-03 11:29:03.371499+05	1	1	2	1	\N
2	400	100	0	5	50	90	2025-08-03 10:00:00+05	videos/2f70bfbc-d2dd-4d5a-b33d-54443a27203f.mov	["agreements/006c509e-acea-4d87-8d6a-6681e1eca696.png"]	t	2025-08-03 11:47:04.200987+05	1	2	2	1	\N
3	400	100	0	5	50	90	2025-08-03 10:00:00+05	videos/eb51622c-b276-4a7d-b357-5af376841499.mov	["agreements/30f522ad-6b2d-430f-b962-9e2aa443a72c.png"]	t	2025-08-03 21:23:58.145361+05	1	1	2	1	\N
4	500	100	0	5	50	120	2025-08-03 10:00:00+05	videos/a5fd0c31-c3dd-4287-b8e7-5851a82ecdb5.mov	["agreements/ef0de1fc-95ca-4933-8de9-e65f4486d37a.png"]	t	2025-08-03 22:13:29.621879+05	3	4	6	2	\N
5	500	100	0	6	50	100	2025-08-03 10:00:00+05	videos/7fa8e7bd-b6f8-4c31-b228-5a2a36e77987.mov	["agreements/fee699db-85d7-4c03-b94f-a2a92024fd53.png"]	t	2025-08-03 22:34:56.274653+05	3	4	6	2	\N
6	500	150	70	3	20	140	2025-08-03 10:00:00+05	videos/ed5fdaad-097f-4ff8-ac23-9c6f54563760.mov	["agreements/726a7bdc-6ac9-40c1-8de2-341547b9b25e.png"]	f	2025-08-03 23:26:44.121277+05	3	4	6	2	\N
7	500	100	0	6	50	100	2025-08-03 10:00:00+05	videos/5b750dde-c5f2-4f94-91ce-c3963bb6b255.mov	["agreements/b2ee9042-eb45-45b9-a9eb-a303882eeb8f.png"]	t	2025-08-04 01:19:43.912882+05	3	4	6	2	\N
8	600	100	0	6	50	125	2025-08-04 10:00:00+05	videos/2b4b079c-535d-449e-a90f-a0fdadbd1bc9.mov	["agreements/a9ca31f7-7492-488f-bc77-53885c006970.png"]	t	2025-08-04 11:19:09.342747+05	3	4	6	2	\N
9	500	100	0	6	50	100	2025-08-04 10:00:00+05	videos/b4019c73-74f4-48f1-9d8a-80d1796e9b3c.mov	["agreements/439d6d03-3a39-4426-b6c2-81982bd8cc48.png"]	t	2025-08-04 12:20:38.1049+05	3	4	6	2	\N
10	500	50	0	6	20	90	2025-08-05 10:00:00+05	\N	["agreements/85d3a3f6-de40-4205-afe1-f4328268114e.jpeg"]	t	2025-08-05 20:12:38.796359+05	3	4	5	2	\N
11	500	100	560	3	40	186.67	2025-08-06 10:00:00+05	\N	["agreements/08b6afd7-755e-49dc-b5da-64b03ed5e689.jpeg"]	f	2025-08-06 21:48:17.799923+05	3	4	5	2	\N
12	700	100	168	5	40	168	2025-08-06 10:00:00+05	videos/9d993c35-7181-4cdd-9faa-135e09523acd.mov	["agreements/54ee7056-a384-4907-894f-862ef1bbc971.png"]	f	2025-08-06 22:19:25.32213+05	1	5	2	1	\N
13	600	100	0	5	40	140	2025-08-06 10:00:00+05	videos/fb517282-5f34-40ff-9b33-89ccf5cc3488.mov	["agreements/0d824f6c-7e03-43c7-b2eb-f71a74e3dd07.png"]	t	2025-08-06 23:58:37.520319+05	1	2	2	1	\N
14	400	100	375	3	25	125	2025-08-09 10:00:00+05	videos/1a79ee18-ed8f-4ac2-b3a5-00f85c85a7ca.mov	["agreements/d659ee53-d34b-401b-9c09-2f2c05069dee.png"]	f	2025-08-09 23:18:42.814057+05	5	6	7	3	\N
15	300	100	240	5	50	60	2025-08-12 10:00:00+05	videos/ba67eefa-226a-4f27-9604-aef4e1c692a1.mov	["agreements/62fb4ebe-a9c4-4157-9153-43a5bf7bc970.jpg"]	f	2025-08-12 12:28:32.845634+05	1	5	2	1	\N
16	1200	300	900	6	40	210	2025-08-28 10:00:00+05	\N	["agreements/475c9bbc-87c9-4b50-8521-f7eeee36834b.jpeg"]	f	2025-08-28 22:37:52.426344+05	7	10	21	17	\N
17	700	300	460	8	50	75	2025-02-25 10:00:00+05	\N	["agreements/375b72b3-43b5-4a10-984a-612d260bafd3.jpeg"]	f	2025-08-28 22:58:11.895822+05	8	10	21	17	\N
18	2300	1200	1155	10	50	165	2025-05-31 10:00:00+05	videos/ad7ecf5f-2c9d-459f-a9d2-d811dc8be066.mov	["agreements/bcd71bf0-ea27-46d7-80fc-54ede05459c4.jpg"]	f	2025-09-01 00:38:41.980844+05	9	5	2	1	1282929281
19	700	300	560	6	40	93.33	2025-09-01 10:00:00+05	\N	\N	f	2025-09-01 15:09:58.232461+05	8	10	21	17	8756
20	600	200	640	3	60	213.33	2025-05-01 10:00:00+05	videos/04329d55-a43c-4205-9d87-046c7a96a6ad.mov	["agreements/4605bb97-76da-449b-a7d5-e27d265c81a0.png"]	f	2025-09-01 17:02:14.140123+05	4	1	2	1	\N
\.


--
-- TOC entry 3535 (class 0 OID 16430)
-- Dependencies: 210
-- Data for Name: magazines; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.magazines (id, name, description, address, phone, status, subscription_end_date, approved_by, created_at, updated_at) FROM stdin;
2	Deana	\N	\N	\N	ACTIVE	2025-11-01	4	2025-08-03 15:40:37+05	2025-08-18 18:38:27+05
4	Uy2	\N	\N	\N	ACTIVE	2025-11-08	4	2025-08-10 10:25:32+05	2025-08-10 10:33:00+05
5	Test	\N	\N	\N	ACTIVE	2025-09-09	4	2025-08-10 10:40:12+05	2025-08-10 10:40:22+05
6	Qoshnim	\N	\N	\N	PENDING	\N	\N	2025-08-10 10:51:31+05	\N
7	Qashqar	\N	\N	\N	PENDING	\N	\N	2025-08-10 10:55:58+05	\N
8	Blyaa	\N	\N	\N	PENDING	\N	\N	2025-08-10 10:56:38+05	\N
9	Jallaaa	\N	\N	\N	PENDING	\N	\N	2025-08-10 11:00:55+05	\N
10	123456	\N	\N	\N	ACTIVE	2026-08-05	4	2025-08-10 11:02:19+05	2025-08-10 11:02:30+05
11	Qodiro	\N	\N	\N	PENDING	\N	\N	2025-08-10 17:58:33+05	\N
12	ishla iltimos	\N	\N	\N	PENDING	\N	\N	2025-08-10 18:04:37+05	\N
13	Qatu ichelik	\N	\N	\N	PENDING	\N	\N	2025-08-10 18:07:41+05	\N
14	Chillabek	\N	\N	\N	ACTIVE	2026-08-15	4	2025-08-20 09:10:06+05	2025-08-20 09:11:19+05
15	Malika	\N	\N	\N	PENDING	\N	\N	2025-08-26 04:51:31+05	\N
16	GameHub	\N	\N	\N	PENDING	\N	\N	2025-08-26 14:49:51+05	\N
17	Smartplus	\N	\N	\N	ACTIVE	2026-08-23	4	2025-08-28 17:29:30+05	2025-08-28 17:33:49+05
18	SnapSell	\N	\N	\N	ACTIVE	2026-08-26	4	2025-08-31 09:28:29+05	2025-08-31 09:28:35+05
19	Garderob	\N	\N	\N	PENDING	\N	\N	2025-09-01 12:09:06.73441+05	\N
20	Test Magazine	\N	\N	\N	PENDING	\N	\N	2025-09-01 12:27:13.611332+05	\N
21	Test Magazine for Notifications	\N	\N	\N	PENDING	\N	\N	2025-09-01 12:43:33.406349+05	\N
22	Updated Test Magazine	\N	\N	\N	PENDING	\N	\N	2025-09-01 12:47:54.156847+05	\N
23	Wolmart	\N	\N	\N	PENDING	\N	\N	2025-09-01 16:28:21.524461+05	\N
1	Metro	\N	\N	\N	ACTIVE	2025-10-02	\N	2025-08-02 13:10:25+05	2025-09-02 17:32:00.317475+05
3	Uy	\N	\N	\N	INACTIVE	2025-09-08	4	2025-08-09 18:07:51+05	2025-09-09 02:00:00.127757+05
24	Chinoz	\N	\N	\N	ACTIVE	2026-09-04	4	2025-09-09 15:23:54.283884+05	2025-09-09 15:29:54.049593+05
\.


--
-- TOC entry 3553 (class 0 OID 16717)
-- Dependencies: 228
-- Data for Name: notification_preferences; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notification_preferences (id, user_id, notification_type, is_enabled, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 3555 (class 0 OID 16731)
-- Dependencies: 230
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, type, title, body, data, recipient_user_id, recipient_role, sender_user_id, push_token_id, status, sent_at, delivered_at, error_message, created_at, updated_at) FROM stdin;
1	new_user_registration	New User Registration	Test User has registered and needs approval	{"userId": "test-123", "userName": "Test User", "userPhone": "+998901234567", "registrationDate": "2025-09-01T07:40:26.314Z"}	4	\N	4	1	failed	\N	\N	0	2025-09-01 12:40:26.458155+05	2025-09-01 12:40:27.112665+05
2	new_user_registration	New User Registration	Test User has registered and needs approval	{"userId": "test-123", "userName": "Test User", "userPhone": "+998901234567", "registrationDate": "2025-09-01T07:40:32.748Z"}	4	\N	4	1	failed	\N	\N	0	2025-09-01 12:40:32.908954+05	2025-09-01 12:40:33.390215+05
3	new_user_registration	New User Registration	Test User has registered and needs approval	{"userId": "test-123", "userName": "Test User", "userPhone": "+998901234567", "registrationDate": "2025-09-01T07:47:20.265Z"}	4	\N	4	1	failed	\N	\N	0	2025-09-01 12:47:20.425739+05	2025-09-01 12:47:20.983457+05
4	new_user_registration	New User Registration	Updated Server Test User has registered and needs approval	{"userId": "30", "userName": "Updated Server Test User", "userPhone": "+998901236666", "registrationDate": "2025-09-01T12:47:54.156847+05:00", "magazineName": "Updated Test Magazine"}	4	\N	\N	1	pending	\N	\N	\N	2025-09-01 12:47:54.530301+05	\N
5	new_user_registration	New User Registration	Test User has registered and needs approval	{"userId": "test-123", "userName": "Test User", "userPhone": "+998901234567", "registrationDate": "2025-09-01T11:26:43.296Z"}	4	\N	4	1	failed	\N	\N	0	2025-09-01 16:26:43.412573+05	2025-09-01 16:26:43.966171+05
6	new_user_registration	New User Registration	Test User has registered and needs approval	{"userId": "test-123", "userName": "Test User", "userPhone": "+998901234567", "registrationDate": "2025-09-01T11:26:52.297Z"}	4	\N	4	1	failed	\N	\N	0	2025-09-01 16:26:52.382545+05	2025-09-01 16:26:52.855824+05
7	new_user_registration	New User Registration	Zubayr Usmonali has registered and needs approval	{"userId": "31", "userName": "Zubayr Usmonali", "userPhone": "+998988808086", "registrationDate": "2025-09-01T16:28:21.524461+05:00", "magazineName": "Wolmart"}	4	\N	\N	1	pending	\N	\N	\N	2025-09-01 16:28:21.86439+05	\N
8	new_user_registration	New User Registration	Test User has registered and needs approval	{"userId": "test-123", "userName": "Test User", "userPhone": "+998901234567", "registrationDate": "2025-09-01T11:41:36.757Z"}	4	\N	4	1	failed	\N	\N	0	2025-09-01 16:41:36.859948+05	2025-09-01 16:41:37.43737+05
9	new_user_registration	New User Registration	Test User has registered and needs approval	{"userId": "test-123", "userName": "Test User", "userPhone": "+998901234567", "registrationDate": "2025-09-02T12:00:07.829Z"}	4	\N	4	1	failed	\N	\N	0	2025-09-02 17:00:08.002005+05	2025-09-02 17:00:08.674636+05
10	new_user_registration	New User Registration	Azizbek Ramizov has registered and needs approval	{"userId": "32", "userName": "Azizbek Ramizov", "userPhone": "+998770730624", "registrationDate": "2025-09-09T15:23:54.283884+05:00", "magazineName": "Chinoz"}	4	\N	\N	33	pending	\N	\N	\N	2025-09-09 15:23:54.636377+05	\N
11	new_user_registration	New User Registration	Azizbek Ramizov has registered and needs approval	{"userId": "32", "userName": "Azizbek Ramizov", "userPhone": "+998770730624", "registrationDate": "2025-09-09T15:23:54.283884+05:00", "magazineName": "Chinoz"}	4	\N	\N	1	pending	\N	\N	\N	2025-09-09 15:23:54.636377+05	\N
\.


--
-- TOC entry 3541 (class 0 OID 16471)
-- Dependencies: 216
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (id, name, model, price, purchase_price, sale_price, count, created_at, updated_at, manager_id) FROM stdin;
2	iPhane 16 pro	Telefon	1280	1024	1280	10	2025-08-03 15:50:03+05	\N	4
3	tv	samsung	500	400	500	9	2025-08-03 16:55:26+05	2025-08-14 23:11:03+05	5
5	Konditsioner	samsung	320	300	320	18	2025-08-09 18:12:48+05	2025-08-09 18:18:42+05	7
6	name	test	300	200	300	9	2025-08-14 20:48:02+05	2025-08-17 10:48:53+05	2
7	iphone	iphone15	1200	1000	1200	0	2025-08-28 17:36:44+05	2025-08-28 17:37:52+05	21
1	Telefon	iphone 11	300	240	300	13	2025-08-03 05:04:03+05	2025-08-31 19:17:10.125317+05	2
10	moshina	nexia3	12000	9000	12000	3	2025-08-31 19:27:34.241816+05	\N	2
11	kiyim	shim	12	10	12	50	2025-08-31 19:29:13.817845+05	\N	2
9	macbook	m1 pro	2300	18000	2300	11	2025-08-31 19:24:55.232416+05	2025-09-01 00:38:41.966641+05	2
12	Samsung	S21	1200	1000	1200	20	2025-09-01 02:07:06.685158+05	\N	5
8	telefon	iphone 15 pro max	700	550	700	2	2025-08-28 17:42:41+05	2025-09-01 15:09:58.217736+05	21
4	kirmoshina	lg	600	500	600	16	2025-08-09 18:03:58+05	2025-09-01 17:02:14.13429+05	2
\.


--
-- TOC entry 3551 (class 0 OID 16700)
-- Dependencies: 226
-- Data for Name: push_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.push_tokens (id, token, user_id, device_type, is_active, created_at, updated_at) FROM stdin;
30	ExponentPushToken[m8DHlTH0M2EyzsxGVAVgeA]	2	mobile	t	2025-09-02 16:37:33.774927+05	2025-09-02 16:37:48.814883+05
32	ExponentPushToken[wWSW-xJzlArrykEhIDKf0b]	5	mobile	t	2025-09-03 19:12:19.668651+05	2025-09-05 20:31:46.249693+05
2	test	30	mobile	t	2025-09-01 12:48:10.956354+05	\N
3	ExponentPushToken[WxmKTmEA6UZIpXBmB0IJmV]	5	mobile	t	2025-09-01 16:25:26.566332+05	2025-09-01 16:28:22.017938+05
33	ExponentPushToken[m8DHlTH0M2EyzsxGVAVgeA]	4	mobile	t	2025-09-04 00:57:40.372314+05	\N
1	ExponentPushToken[wWSW-xJzlArrykEhIDKf0b]	4	mobile	t	2025-09-01 12:24:11.961071+05	2025-09-01 16:46:00.024861+05
34	ExponentPushToken[qNlKEgMoUQzhGgEtC4Dbee]	2	mobile	t	2025-09-04 12:58:53.441531+05	2025-09-09 03:41:45.573222+05
31	ExponentPushToken[wWSW-xJzlArrykEhIDKf0b]	2	mobile	t	2025-09-02 17:20:05.200364+05	2025-09-09 15:38:49.432936+05
\.


--
-- TOC entry 3543 (class 0 OID 16488)
-- Dependencies: 218
-- Data for Name: sales; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sales (id, sale_price, sale_date, created_at, product_id, seller_id, magazine_id, imei) FROM stdin;
1	350	2025-08-03 10:04:16.131381+05	2025-08-03 10:04:16.131387+05	1	2	1	\N
2	500	2025-08-05 20:16:27.282181+05	2025-08-05 20:16:27.282188+05	3	5	2	\N
3	520	2025-08-05 20:17:03.243012+05	2025-08-05 20:17:03.243018+05	3	5	2	\N
4	500	2025-08-06 22:18:30.204884+05	2025-08-06 22:18:30.204888+05	1	2	1	\N
5	300	2025-08-06 22:24:43.899474+05	2025-08-06 22:24:43.899477+05	1	2	1	\N
6	300	2025-08-06 22:24:49.931628+05	2025-08-06 22:24:49.931633+05	1	2	1	\N
7	300	2025-08-06 22:24:56.033246+05	2025-08-06 22:24:56.033251+05	1	2	1	\N
8	300	2025-08-06 22:25:05.212091+05	2025-08-06 22:25:05.212095+05	1	2	1	\N
9	300	2025-08-06 22:25:12.769445+05	2025-08-06 22:25:12.769453+05	1	2	1	\N
10	600	2025-08-06 22:29:25.689481+05	2025-08-06 22:29:25.689485+05	1	2	1	\N
11	800	2025-08-06 22:29:41.147537+05	2025-08-06 22:29:41.147542+05	1	2	1	\N
12	200	2025-08-06 22:29:45.834166+05	2025-08-06 22:29:45.83418+05	1	2	1	\N
13	900	2025-08-06 22:49:50.544777+05	2025-08-06 22:49:50.544782+05	1	2	1	\N
14	400	2025-08-06 22:50:03.406933+05	2025-08-06 22:50:03.406939+05	1	2	1	\N
15	380	2025-08-06 22:50:09.357684+05	2025-08-06 22:50:09.357688+05	1	2	1	\N
16	240	2025-08-06 22:50:14.426766+05	2025-08-06 22:50:14.426771+05	1	2	1	\N
17	370	2025-08-06 22:50:19.803837+05	2025-08-06 22:50:19.803843+05	1	2	1	\N
18	652	2025-08-06 22:50:24.496728+05	2025-08-06 22:50:24.496734+05	1	2	1	\N
19	214	2025-08-06 22:50:29.682385+05	2025-08-06 22:50:29.68239+05	1	2	1	\N
20	850	2025-08-06 22:50:34.638212+05	2025-08-06 22:50:34.638218+05	1	2	1	\N
21	369	2025-08-06 22:51:31.049197+05	2025-08-06 22:51:31.049201+05	1	2	1	\N
22	600	2025-08-09 23:04:10.751063+05	2025-08-09 23:04:10.751069+05	4	2	1	\N
23	325	2025-08-09 23:12:56.035216+05	2025-08-09 23:12:56.035221+05	5	7	3	\N
24	650	2025-08-13 16:53:51.002639+05	2025-08-13 16:53:51.002645+05	4	2	1	\N
25	300	2025-08-15 04:10:29.706589+05	2025-08-15 04:10:29.706595+05	1	2	1	\N
26	500	2025-08-15 04:11:03.299114+05	2025-08-15 04:11:03.29912+05	3	6	2	\N
27	300	2025-08-17 15:48:53.577656+05	2025-08-17 15:48:53.577663+05	6	2	1	\N
28	700	2025-08-28 22:43:28.559004+05	2025-08-28 22:43:28.559009+05	8	21	17	\N
29	550	2025-08-28 22:43:40.906057+05	2025-08-28 22:43:40.906062+05	4	2	1	\N
30	300	2025-08-31 19:17:10.135828+05	2025-08-31 19:17:10.135834+05	1	2	1	1123826371
\.


--
-- TOC entry 3549 (class 0 OID 16556)
-- Dependencies: 224
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.transactions (id, type, amount, description, created_at, sale_id, loan_id, loan_payment_id, product_id, client_id, seller_id, magazine_id) FROM stdin;
1	SALE	350	Sale of Telefon iphone 11	2025-08-03 10:04:16.142838+05	1	\N	\N	1	\N	2	1
2	LOAN	300	Loan created for Azim - Telefon iphone 11	2025-08-03 11:29:03.391034+05	\N	1	\N	1	1	2	1
3	LOAN	400	Loan created for Shaxzod - Telefon iphone 11	2025-08-03 11:47:04.20973+05	\N	2	\N	1	2	2	1
4	LOAN_PAYMENT	90	Payment received for loan #2 - Shaxzod	2025-08-03 11:47:56.545862+05	\N	2	6	\N	2	2	1
5	LOAN_PAYMENT	210	Full loan payment for loan #2 - Shaxzod (Loan completed)	2025-08-03 11:48:27.930297+05	\N	2	\N	\N	2	2	1
6	LOAN_PAYMENT	72.5	Payment received for loan #1 - Azim	2025-08-03 11:50:00.350266+05	\N	1	1	\N	1	2	1
7	LOAN_PAYMENT	72.5	Payment received for loan #1 - Azim	2025-08-03 12:06:57.79273+05	\N	1	2	\N	1	2	1
8	LOAN_PAYMENT	105	Full loan payment for loan #1 - Azim (Loan completed)	2025-08-03 12:07:58.689749+05	\N	1	\N	\N	1	2	1
9	LOAN	400	Loan created for Azim - Telefon iphone 11	2025-08-03 21:23:58.160318+05	\N	3	\N	1	1	2	1
10	LOAN	500	Loan created for Shaxzod - tv samsung	2025-08-03 22:13:29.640084+05	\N	4	\N	3	4	6	2
11	LOAN_PAYMENT	130	Payment received for loan #4 - Shaxzod	2025-08-03 22:19:24.069038+05	\N	4	18	\N	4	6	2
12	LOAN_PAYMENT	270	Full loan payment for loan #4 - Shaxzod (Loan completed)	2025-08-03 22:20:32.432514+05	\N	4	\N	\N	4	6	2
13	LOAN	500	Loan created for Shaxzod - tv samsung	2025-08-03 22:34:56.29904+05	\N	5	\N	3	4	6	2
14	LOAN_PAYMENT	600	Payment received for loan #5 - Shaxzod	2025-08-03 23:24:26.481354+05	\N	5	24	\N	4	6	2
15	LOAN	500	Loan created for Shaxzod - tv samsung	2025-08-03 23:26:44.13262+05	\N	6	\N	3	4	6	2
16	LOAN_PAYMENT	140	Payment received for loan #6 - Shaxzod	2025-08-03 23:29:20.640006+05	\N	6	30	\N	4	6	2
17	LOAN	500	Loan created for Shaxzod - tv samsung	2025-08-04 01:19:43.928364+05	\N	7	\N	3	4	6	2
18	LOAN_PAYMENT	100	Payment received for loan #7 - Shaxzod	2025-08-04 01:20:30.772725+05	\N	7	33	\N	4	6	2
19	LOAN_PAYMENT	550	Payment received for loan #7 - Shaxzod	2025-08-04 01:21:24.894301+05	\N	7	34	\N	4	6	2
20	LOAN_PAYMENT	100	Payment received for loan #7 - Shaxzod	2025-08-04 01:21:38.497091+05	\N	7	35	\N	4	6	2
21	LOAN	600	Loan created for Shaxzod - tv samsung	2025-08-04 11:19:09.359515+05	\N	8	\N	3	4	6	2
22	LOAN_PAYMENT	125	Payment received for loan #8 - Shaxzod	2025-08-04 11:21:09.362269+05	\N	8	39	\N	4	6	2
23	LOAN_PAYMENT	625	Full loan payment for loan #8 - Shaxzod (Loan completed)	2025-08-04 11:42:12.115023+05	\N	8	\N	\N	4	6	2
24	LOAN	500	Loan created for Shaxzod - tv samsung	2025-08-04 12:20:38.123363+05	\N	9	\N	3	4	6	2
25	LOAN_PAYMENT	500	Full loan payment for loan #9 - Shaxzod (Loan completed)	2025-08-04 12:28:37.258412+05	\N	9	\N	\N	4	6	2
26	LOAN_PAYMENT	140	Payment received for loan #6 - Shaxzod	2025-08-04 12:28:59.087013+05	\N	6	31	\N	4	6	2
27	LOAN	500	Loan created for Shaxzod - tv samsung	2025-08-05 20:12:38.811196+05	\N	10	\N	3	4	5	2
28	LOAN_PAYMENT	520	Full loan payment for loan #10 - Shaxzod (Loan completed)	2025-08-05 20:13:33.937944+05	\N	10	\N	\N	4	5	2
29	SALE	500	Sale of tv samsung	2025-08-05 20:16:27.289605+05	2	\N	\N	3	\N	5	2
30	SALE	520	Sale of tv samsung	2025-08-05 20:17:03.251+05	3	\N	\N	3	\N	5	2
31	LOAN	500	Loan created for Shaxzod - tv samsung	2025-08-06 21:48:17.812012+05	\N	11	\N	3	4	5	2
32	LOAN_PAYMENT	90	Payment received for loan #3 - Azim	2025-08-06 22:16:48.88606+05	\N	3	13	\N	1	2	1
33	SALE	500	Sale of Telefon iphone 11	2025-08-06 22:18:30.211184+05	4	\N	\N	1	\N	2	1
34	LOAN	700	Loan created for Giyos - Telefon iphone 11	2025-08-06 22:19:25.334626+05	\N	12	\N	1	5	2	1
35	LOAN_PAYMENT	168	Payment received for loan #12 - Giyos	2025-08-06 22:24:02.762582+05	\N	12	63	\N	5	2	1
36	SALE	300	Sale of Telefon iphone 11	2025-08-06 22:24:43.904344+05	5	\N	\N	1	\N	2	1
37	SALE	300	Sale of Telefon iphone 11	2025-08-06 22:24:49.938455+05	6	\N	\N	1	\N	2	1
38	SALE	300	Sale of Telefon iphone 11	2025-08-06 22:24:56.038134+05	7	\N	\N	1	\N	2	1
39	SALE	300	Sale of Telefon iphone 11	2025-08-06 22:25:05.216278+05	8	\N	\N	1	\N	2	1
40	SALE	300	Sale of Telefon iphone 11	2025-08-06 22:25:12.774457+05	9	\N	\N	1	\N	2	1
41	SALE	600	Sale of Telefon iphone 11	2025-08-06 22:29:25.694478+05	10	\N	\N	1	\N	2	1
42	SALE	800	Sale of Telefon iphone 11	2025-08-06 22:29:41.152341+05	11	\N	\N	1	\N	2	1
43	SALE	200	Sale of Telefon iphone 11	2025-08-06 22:29:45.838329+05	12	\N	\N	1	\N	2	1
44	SALE	900	Sale of Telefon iphone 11	2025-08-06 22:49:50.552407+05	13	\N	\N	1	\N	2	1
45	SALE	400	Sale of Telefon iphone 11	2025-08-06 22:50:03.414714+05	14	\N	\N	1	\N	2	1
46	SALE	380	Sale of Telefon iphone 11	2025-08-06 22:50:09.361526+05	15	\N	\N	1	\N	2	1
47	SALE	240	Sale of Telefon iphone 11	2025-08-06 22:50:14.435056+05	16	\N	\N	1	\N	2	1
48	SALE	370	Sale of Telefon iphone 11	2025-08-06 22:50:19.807994+05	17	\N	\N	1	\N	2	1
49	SALE	652	Sale of Telefon iphone 11	2025-08-06 22:50:24.501335+05	18	\N	\N	1	\N	2	1
50	SALE	214	Sale of Telefon iphone 11	2025-08-06 22:50:29.686069+05	19	\N	\N	1	\N	2	1
51	SALE	850	Sale of Telefon iphone 11	2025-08-06 22:50:34.646074+05	20	\N	\N	1	\N	2	1
52	SALE	369	Sale of Telefon iphone 11	2025-08-06 22:51:31.053466+05	21	\N	\N	1	\N	2	1
53	LOAN	600	Loan created for Shaxzod - Telefon iphone 11	2025-08-06 23:58:37.557276+05	\N	13	\N	1	2	2	1
54	SALE	600	Sale of kirmoshina lg	2025-08-09 23:04:10.758816+05	22	\N	\N	4	\N	2	1
55	SALE	325	Sale of Konditsioner samsung	2025-08-09 23:12:56.042877+05	23	\N	\N	5	\N	7	3
56	LOAN	400	Loan created for Nodir - Konditsioner samsung	2025-08-09 23:18:42.831065+05	\N	14	\N	5	6	7	3
57	LOAN_PAYMENT	700	Full loan payment for loan #13 - Shaxzod (Loan completed)	2025-08-11 13:43:10.216242+05	\N	13	\N	\N	2	2	1
58	LOAN	300	Loan created for Giyos - Telefon iphone 11	2025-08-12 12:28:32.861707+05	\N	15	\N	1	5	2	1
59	LOAN_PAYMENT	60	Payment received for loan #15 - Giyos	2025-08-12 12:28:43.418494+05	\N	15	77	\N	5	2	1
60	SALE	650	Sale of kirmoshina lg	2025-08-13 16:53:51.013334+05	24	\N	\N	4	\N	2	1
61	SALE	300	Sale of Telefon iphone 11	2025-08-15 04:10:29.717159+05	25	\N	\N	1	\N	2	1
62	SALE	500	Sale of tv samsung	2025-08-15 04:11:03.309387+05	26	\N	\N	3	\N	6	2
63	SALE	300	Sale of name test	2025-08-17 15:48:53.587937+05	27	\N	\N	6	\N	2	1
64	LOAN_PAYMENT	210	Full loan payment for loan #3 - Azim (Loan completed)	2025-08-17 15:51:28.950101+05	\N	3	\N	\N	1	2	1
65	LOAN	1200	Loan created for Abdulaziz - iphone iphone15	2025-08-28 22:37:52.449545+05	\N	16	\N	7	10	21	17
66	LOAN_PAYMENT	210	Payment received for loan #16 - Abdulaziz	2025-08-28 22:39:26.358819+05	\N	16	83	\N	10	21	17
67	SALE	700	Sale of telefon iphone 15 pro max	2025-08-28 22:43:28.565443+05	28	\N	\N	8	\N	21	17
68	SALE	550	Sale of kirmoshina lg	2025-08-28 22:43:40.912007+05	29	\N	\N	4	\N	2	1
69	LOAN	700	Loan created for Abdulaziz - telefon iphone 15 pro max	2025-08-28 22:58:11.909949+05	\N	17	\N	8	10	21	17
70	LOAN_PAYMENT	60	Payment received for loan #17 - Abdulaziz	2025-08-28 22:58:48.007876+05	\N	17	89	\N	10	21	17
71	LOAN_PAYMENT	80	Payment received for loan #17 - Abdulaziz	2025-08-28 23:02:13.279107+05	\N	17	90	\N	10	21	17
72	LOAN_PAYMENT	168	Payment received for loan #12 - Giyos	2025-08-28 23:03:39.062492+05	\N	12	64	\N	5	2	1
73	LOAN_PAYMENT	168	Payment received for loan #12 - Giyos	2025-08-28 23:03:44.338261+05	\N	12	65	\N	5	2	1
74	LOAN_PAYMENT	168	Payment received for loan #12 - Giyos	2025-08-28 23:03:48.486204+05	\N	12	66	\N	5	2	1
75	LOAN_PAYMENT	150	Payment received for loan #16 - Abdulaziz	2025-08-29 19:01:46.178325+05	\N	16	84	\N	10	21	17
76	SALE	300	Sale of Telefon iphone 11	2025-08-31 19:17:10.14673+05	30	\N	\N	1	\N	2	1
77	LOAN	2300	Loan created for Giyos - macbook m1 pro	2025-09-01 00:38:42.003378+05	\N	18	\N	9	5	2	1
78	LOAN_PAYMENT	165	Payment received for loan #18 - Giyos	2025-09-01 03:35:16.756492+05	\N	18	97	\N	5	2	1
79	LOAN_PAYMENT	165	Payment received for loan #18 - Giyos	2025-09-01 10:53:12.338867+05	\N	18	98	\N	5	2	1
80	LOAN_PAYMENT	165	Payment received for loan #18 - Giyos	2025-09-01 11:22:17.618426+05	\N	18	99	\N	5	2	1
81	LOAN	700	Loan created for Abdulaziz - telefon iphone 15 pro max	2025-09-01 15:09:58.263054+05	\N	19	\N	8	10	21	17
82	LOAN	600	Loan created for Azim - kirmoshina lg	2025-09-01 17:02:14.152729+05	\N	20	\N	4	1	2	1
\.


--
-- TOC entry 3537 (class 0 OID 16442)
-- Dependencies: 212
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, name, phone, password_hash, role, status, magazine_name, subscription_end_date, created_at, updated_at, magazine_id, manager_id, user_type) FROM stdin;
3	Admin	+998998901234567	$2b$12$mdO/DPk1K9CyhJPelsc6Yup5uga2NxbZU/zVNlUo7b1w/qTRgyO4O	ADMIN	ACTIVE	\N	\N	2025-08-02 13:14:25+05	\N	\N	\N	gadgets
4	Admin	+998901234567	$2b$12$XHE2bvl94xzU/4dUqRgLnucB2ujGSHQ6spGCkf4OkKeiVORPDLbVu	ADMIN	ACTIVE	\N	\N	2025-08-02 13:23:48+05	\N	\N	\N	gadgets
29	Real Test User for Admin Alert	+998901235555	$2b$12$CB3k7.x54BhIZyxt1.jdrOcIVSqIILhUnBOHT6zIjvKsbonZ36mvK	MANAGER	PENDING	\N	\N	2025-09-01 12:43:33.406349+05	\N	21	\N	gadgets
5	Zubayr Usmonali	+998910188181	$2b$12$doLIc1sP8pg60o4EdleGIONNIGQLDNwjke1/DqauWoe/e7hztKVAq	MANAGER	ACTIVE	\N	2025-11-01	2025-08-03 15:40:37+05	2025-08-18 18:38:27+05	2	\N	gadgets
6	Abdusattor	+998900188181	$2b$12$23G4c8HL/GAn67eQ3BikYupktcNkZZcXKGP1GQ/g6Fy4ZIs5rCrs2	SELLER	ACTIVE	\N	\N	2025-08-03 15:42:59+05	2025-08-18 18:37:16+05	2	5	gadgets
8	Domashniy	+998944221266	$2b$12$x0UR5fy8KVfyVS6EF37tquuzU/2OMyYoRFUHW.5BSaqGst8DhSRIy	MANAGER	ACTIVE	\N	2025-11-08	2025-08-10 10:25:32+05	2025-08-10 10:33:00+05	4	\N	gadgets
9	Rovshan	+998997654321	$2b$12$KAGVjOnPTI7pwpw9gvJJ2Of2MAdsvc4ei0/rAnAIaoXDjkf3r7ht2	MANAGER	ACTIVE	\N	2025-09-09	2025-08-10 10:40:12+05	2025-08-10 10:40:22+05	5	\N	gadgets
10	Qahramoniy	+998950489840	$2b$12$j0Ucdz9.RlWXgXiI.gZtKu5g9wIh6i.qv1Om5dl.lzJ0rUFP2zJMG	MANAGER	PENDING	\N	\N	2025-08-10 10:51:31+05	\N	6	\N	gadgets
11	Qashqar	+998987654321	$2b$12$R/VJGrm57tKmxyoJY90Qm.YNoT9.bifsgqs6XyMufC7LmiLDJ1kgm	MANAGER	PENDING	\N	\N	2025-08-10 10:55:59+05	\N	7	\N	gadgets
12	Blya	+998977654321	$2b$12$tRJicuLxYks7dG/h/8ttPuRkn9vUgDvLdZ2g3NrIVhRG6K0q6MAkm	MANAGER	PENDING	\N	\N	2025-08-10 10:56:39+05	\N	8	\N	gadgets
13	Suka	+998967654321	$2b$12$TKweOFnPOVIM.9QnL3IcQO1YrltATpIJl3dCwDKT8V4Jzm45StKba	MANAGER	PENDING	\N	\N	2025-08-10 11:00:56+05	\N	9	\N	gadgets
14	Obbbooo	+998957654321	$2b$12$9i9qbnuf3BrF/7Z7lE5OZuoUb1SP5iVLK/D6CrvmHZNz/Rf7ysyOu	MANAGER	ACTIVE	\N	2026-08-05	2025-08-10 11:02:20+05	2025-08-10 11:02:30+05	10	\N	gadgets
15	Qodirbek	+998937654321	$2b$12$cgYEU2oEx7kIrfpCjiNbme41WGifMr8jbREE9FzR0nY8l.QK7IvIu	MANAGER	PENDING	\N	\N	2025-08-10 17:58:33+05	\N	11	\N	gadgets
16	Zaebal	+998917654321	$2b$12$arMAw5uZqX82QnJRJspD6OJiMYN8fi9NyZtzFznLRFFoYXCwEmzZm	MANAGER	PENDING	\N	\N	2025-08-10 18:04:37+05	\N	12	\N	gadgets
17	Yebanmisa	+998927654321	$2b$12$jlvQIzOMidNFK20zL2L8t.Pa7yeAexiUwTo.JbBpiB9r74z66grie	MANAGER	PENDING	\N	\N	2025-08-10 18:07:41+05	\N	13	\N	gadgets
18	Musaxon	+998940489840	$2b$12$Q49hxFcI0T2w.JpO8ApnduiCPcRHuchuWwe1l2pWe1sZ4Q1SjgHo2	MANAGER	ACTIVE	\N	2026-08-15	2025-08-20 09:10:06+05	2025-08-20 09:11:19+05	14	\N	gadgets
19	Oybek	+998950098998	$2b$12$CG97z4mnn./x791BMk0AEumJtgyfL6YrrAwKARxCuehuWarRMfYCq	MANAGER	PENDING	\N	\N	2025-08-26 04:51:31+05	\N	15	\N	gadgets
20	Boqijonov Otabek	+998998037883	$2b$12$t8r5CKTXBrmcv2AEmieGZOXnjmbKAZW6.0dhA/1rScTRgATiL1B0.	MANAGER	PENDING	\N	\N	2025-08-26 14:49:51+05	\N	16	\N	gadgets
21	Abdulhamid	+998998107348	$2b$12$Fb1zvUILEaZzfkSEPsm/o.BRME54zhrGZ5Yzo7YTkPRoE/fpyW8Se	MANAGER	ACTIVE	\N	2026-08-23	2025-08-28 17:29:31+05	2025-08-28 17:33:49+05	17	\N	gadgets
22	Azimjon	+998994090129	$2b$12$98vDx4vXhKDn.xVfWjCxNuebr/daKFZriXdlL9pHGagPHOuOMR6rC	MANAGER	ACTIVE	\N	2026-08-26	2025-08-31 09:28:30+05	2025-08-31 09:28:35+05	18	\N	gadgets
23	Admin	+99801234567	$2b$12$3qxELSpFuFqFgaKvjwMVOO88NfXEu3a5TgAE4P01rZRwPV393gce.	ADMIN	ACTIVE	\N	\N	2025-08-31 18:32:24.37727+05	\N	\N	\N	gadgets
1	Admin	+998admin	$2b$12$LMm74wPxZ9fmNjUVDteqN.FSubMCZ4kwlUYjB9Y8dXK1gFHYqG8Qi	ADMIN	ACTIVE	\N	\N	2025-08-02 07:13:35+05	2025-09-01 12:04:53.866944+05	\N	\N	gadgets
27	Mamardashvili	+998012345678	$2b$12$QApKyGY4xj70njk8p3DnzOor3YrdWtZKPziYOJbQbMXxbx..GJi/u	MANAGER	PENDING	\N	\N	2025-09-01 12:09:06.73441+05	\N	19	\N	gadgets
28	Test User for Notifications	+998901234999	$2b$12$KWUzpMHObmOP6ptiGJQeBOtdce5ZBKdXJquen61ziu5t.ZrdoWx3S	MANAGER	PENDING	\N	\N	2025-09-01 12:27:13.611332+05	\N	20	\N	gadgets
30	Updated Server Test User	+998901236666	$2b$12$3x51G8ccJPbDjSjCZd8v2OArs7BoOWQC6yHd1wgivNXWTKvB.Qx4C	MANAGER	PENDING	Updated Test Magazine	\N	2025-09-01 12:47:54.156847+05	2025-09-01 12:47:54.530301+05	22	\N	gadgets
31	Zubayr Usmonali	+998988808086	$2b$12$9yKu/bvYb4VpOP5dgsUbIOa4BvmiQJ6K.X3yaV2xy4rmtWL2X2YZu	MANAGER	PENDING	Wolmart	\N	2025-09-01 16:28:21.524461+05	2025-09-01 16:28:21.86439+05	23	\N	gadgets
2	PostgreSQL Test User	+998903335644	$2b$12$8G4vS7vSLPTXSCPh/vFk0Og4d9ffMFC/EHQBwKcQoJPksGFa5TuHG	MANAGER	ACTIVE	\N	2025-10-02	2025-08-02 13:10:25+05	2025-09-02 17:32:00.317475+05	1	\N	gadgets
7	Shaxzod	+998931061613	$2b$12$qHhseH5z6Es48sWYRnm2xu.xj18L57XK324ZPKgMMNb6olvwxnlVu	MANAGER	INACTIVE	\N	2025-09-08	2025-08-09 18:07:51+05	2025-09-09 02:00:00.127757+05	3	\N	gadgets
32	Azizbek Ramizov	+998770730624	$2b$12$s7pEyrfJedATLS9mqVQZ8ebZehPo4IivshCoUyImEDzIthV9AYeJm	MANAGER	ACTIVE	Chinoz	2026-09-04	2025-09-09 15:23:54.283884+05	2025-09-09 15:29:54.049593+05	24	\N	gadgets
\.


--
-- TOC entry 3584 (class 0 OID 0)
-- Dependencies: 237
-- Name: auto_loan_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auto_loan_payments_id_seq', 1, false);


--
-- TOC entry 3585 (class 0 OID 0)
-- Dependencies: 235
-- Name: auto_loans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auto_loans_id_seq', 1, false);


--
-- TOC entry 3586 (class 0 OID 0)
-- Dependencies: 231
-- Name: auto_products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auto_products_id_seq', 1, false);


--
-- TOC entry 3587 (class 0 OID 0)
-- Dependencies: 233
-- Name: auto_sales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auto_sales_id_seq', 1, false);


--
-- TOC entry 3588 (class 0 OID 0)
-- Dependencies: 213
-- Name: clients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.clients_id_seq', 12, true);


--
-- TOC entry 3589 (class 0 OID 0)
-- Dependencies: 221
-- Name: loan_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.loan_payments_id_seq', 115, true);


--
-- TOC entry 3590 (class 0 OID 0)
-- Dependencies: 219
-- Name: loans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.loans_id_seq', 20, true);


--
-- TOC entry 3591 (class 0 OID 0)
-- Dependencies: 209
-- Name: magazines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.magazines_id_seq', 41, true);


--
-- TOC entry 3592 (class 0 OID 0)
-- Dependencies: 227
-- Name: notification_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notification_preferences_id_seq', 1, false);


--
-- TOC entry 3593 (class 0 OID 0)
-- Dependencies: 229
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notifications_id_seq', 11, true);


--
-- TOC entry 3594 (class 0 OID 0)
-- Dependencies: 215
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_id_seq', 12, true);


--
-- TOC entry 3595 (class 0 OID 0)
-- Dependencies: 225
-- Name: push_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.push_tokens_id_seq', 34, true);


--
-- TOC entry 3596 (class 0 OID 0)
-- Dependencies: 217
-- Name: sales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sales_id_seq', 30, true);


--
-- TOC entry 3597 (class 0 OID 0)
-- Dependencies: 223
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.transactions_id_seq', 82, true);


--
-- TOC entry 3598 (class 0 OID 0)
-- Dependencies: 211
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 32, true);


--
-- TOC entry 3357 (class 2606 OID 17100)
-- Name: auto_loan_payments auto_loan_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loan_payments
    ADD CONSTRAINT auto_loan_payments_pkey PRIMARY KEY (id);


--
-- TOC entry 3351 (class 2606 OID 17067)
-- Name: auto_loans auto_loans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loans
    ADD CONSTRAINT auto_loans_pkey PRIMARY KEY (id);


--
-- TOC entry 3342 (class 2606 OID 17025)
-- Name: auto_products auto_products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_products
    ADD CONSTRAINT auto_products_pkey PRIMARY KEY (id);


--
-- TOC entry 3346 (class 2606 OID 17041)
-- Name: auto_sales auto_sales_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_sales
    ADD CONSTRAINT auto_sales_pkey PRIMARY KEY (id);


--
-- TOC entry 3308 (class 2606 OID 16462)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- TOC entry 3325 (class 2606 OID 16548)
-- Name: loan_payments loan_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loan_payments
    ADD CONSTRAINT loan_payments_pkey PRIMARY KEY (id);


--
-- TOC entry 3322 (class 2606 OID 16518)
-- Name: loans loans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_pkey PRIMARY KEY (id);


--
-- TOC entry 3302 (class 2606 OID 16438)
-- Name: magazines magazines_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.magazines
    ADD CONSTRAINT magazines_pkey PRIMARY KEY (id);


--
-- TOC entry 3337 (class 2606 OID 16723)
-- Name: notification_preferences notification_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification_preferences
    ADD CONSTRAINT notification_preferences_pkey PRIMARY KEY (id);


--
-- TOC entry 3340 (class 2606 OID 16739)
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- TOC entry 3314 (class 2606 OID 16479)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 3332 (class 2606 OID 16708)
-- Name: push_tokens push_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_tokens
    ADD CONSTRAINT push_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 3318 (class 2606 OID 16493)
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (id);


--
-- TOC entry 3328 (class 2606 OID 16563)
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- TOC entry 3334 (class 2606 OID 16759)
-- Name: push_tokens uq_user_token; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_tokens
    ADD CONSTRAINT uq_user_token UNIQUE (user_id, token);


--
-- TOC entry 3306 (class 2606 OID 16450)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3358 (class 1259 OID 17113)
-- Name: idx_auto_loan_payments_auto_loan_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_loan_payments_auto_loan_id ON public.auto_loan_payments USING btree (auto_loan_id);


--
-- TOC entry 3359 (class 1259 OID 17114)
-- Name: idx_auto_loan_payments_due_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_loan_payments_due_date ON public.auto_loan_payments USING btree (due_date);


--
-- TOC entry 3360 (class 1259 OID 17115)
-- Name: idx_auto_loan_payments_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_loan_payments_status ON public.auto_loan_payments USING btree (status);


--
-- TOC entry 3352 (class 1259 OID 17109)
-- Name: idx_auto_loans_auto_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_loans_auto_product_id ON public.auto_loans USING btree (auto_product_id);


--
-- TOC entry 3353 (class 1259 OID 17110)
-- Name: idx_auto_loans_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_loans_client_id ON public.auto_loans USING btree (client_id);


--
-- TOC entry 3354 (class 1259 OID 17112)
-- Name: idx_auto_loans_loan_start_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_loans_loan_start_date ON public.auto_loans USING btree (loan_start_date);


--
-- TOC entry 3355 (class 1259 OID 17111)
-- Name: idx_auto_loans_seller_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_loans_seller_id ON public.auto_loans USING btree (seller_id);


--
-- TOC entry 3343 (class 1259 OID 17031)
-- Name: idx_auto_products_car_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_products_car_name ON public.auto_products USING btree (car_name);


--
-- TOC entry 3344 (class 1259 OID 17032)
-- Name: idx_auto_products_manager_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_products_manager_id ON public.auto_products USING btree (manager_id);


--
-- TOC entry 3347 (class 1259 OID 17106)
-- Name: idx_auto_sales_auto_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_sales_auto_product_id ON public.auto_sales USING btree (auto_product_id);


--
-- TOC entry 3348 (class 1259 OID 17108)
-- Name: idx_auto_sales_sale_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_sales_sale_date ON public.auto_sales USING btree (sale_date);


--
-- TOC entry 3349 (class 1259 OID 17107)
-- Name: idx_auto_sales_seller_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_auto_sales_seller_id ON public.auto_sales USING btree (seller_id);


--
-- TOC entry 3319 (class 1259 OID 16666)
-- Name: idx_loans_imei; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_loans_imei ON public.loans USING btree (imei);


--
-- TOC entry 3315 (class 1259 OID 16665)
-- Name: idx_sales_imei; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sales_imei ON public.sales USING btree (imei);


--
-- TOC entry 3309 (class 1259 OID 16468)
-- Name: ix_clients_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clients_id ON public.clients USING btree (id);


--
-- TOC entry 3310 (class 1259 OID 16469)
-- Name: ix_clients_passport_series; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_clients_passport_series ON public.clients USING btree (passport_series);


--
-- TOC entry 3323 (class 1259 OID 16554)
-- Name: ix_loan_payments_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_loan_payments_id ON public.loan_payments USING btree (id);


--
-- TOC entry 3320 (class 1259 OID 16539)
-- Name: ix_loans_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_loans_id ON public.loans USING btree (id);


--
-- TOC entry 3299 (class 1259 OID 16440)
-- Name: ix_magazines_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_magazines_id ON public.magazines USING btree (id);


--
-- TOC entry 3300 (class 1259 OID 16439)
-- Name: ix_magazines_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_magazines_name ON public.magazines USING btree (name);


--
-- TOC entry 3335 (class 1259 OID 16729)
-- Name: ix_notification_preferences_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notification_preferences_id ON public.notification_preferences USING btree (id);


--
-- TOC entry 3338 (class 1259 OID 16755)
-- Name: ix_notifications_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_id ON public.notifications USING btree (id);


--
-- TOC entry 3311 (class 1259 OID 16485)
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_products_id ON public.products USING btree (id);


--
-- TOC entry 3312 (class 1259 OID 16486)
-- Name: ix_products_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_products_name ON public.products USING btree (name);


--
-- TOC entry 3329 (class 1259 OID 16714)
-- Name: ix_push_tokens_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_push_tokens_id ON public.push_tokens USING btree (id);


--
-- TOC entry 3330 (class 1259 OID 16760)
-- Name: ix_push_tokens_token; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_push_tokens_token ON public.push_tokens USING btree (token);


--
-- TOC entry 3316 (class 1259 OID 16509)
-- Name: ix_sales_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sales_id ON public.sales USING btree (id);


--
-- TOC entry 3326 (class 1259 OID 16599)
-- Name: ix_transactions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_transactions_id ON public.transactions USING btree (id);


--
-- TOC entry 3303 (class 1259 OID 16451)
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- TOC entry 3304 (class 1259 OID 16452)
-- Name: ix_users_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_phone ON public.users USING btree (phone);


--
-- TOC entry 3394 (class 2606 OID 17101)
-- Name: auto_loan_payments auto_loan_payments_auto_loan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loan_payments
    ADD CONSTRAINT auto_loan_payments_auto_loan_id_fkey FOREIGN KEY (auto_loan_id) REFERENCES public.auto_loans(id);


--
-- TOC entry 3390 (class 2606 OID 17068)
-- Name: auto_loans auto_loans_auto_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loans
    ADD CONSTRAINT auto_loans_auto_product_id_fkey FOREIGN KEY (auto_product_id) REFERENCES public.auto_products(id);


--
-- TOC entry 3391 (class 2606 OID 17073)
-- Name: auto_loans auto_loans_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loans
    ADD CONSTRAINT auto_loans_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 3392 (class 2606 OID 17083)
-- Name: auto_loans auto_loans_magazine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loans
    ADD CONSTRAINT auto_loans_magazine_id_fkey FOREIGN KEY (magazine_id) REFERENCES public.magazines(id);


--
-- TOC entry 3393 (class 2606 OID 17078)
-- Name: auto_loans auto_loans_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_loans
    ADD CONSTRAINT auto_loans_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- TOC entry 3386 (class 2606 OID 17026)
-- Name: auto_products auto_products_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_products
    ADD CONSTRAINT auto_products_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- TOC entry 3387 (class 2606 OID 17042)
-- Name: auto_sales auto_sales_auto_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_sales
    ADD CONSTRAINT auto_sales_auto_product_id_fkey FOREIGN KEY (auto_product_id) REFERENCES public.auto_products(id);


--
-- TOC entry 3388 (class 2606 OID 17052)
-- Name: auto_sales auto_sales_magazine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_sales
    ADD CONSTRAINT auto_sales_magazine_id_fkey FOREIGN KEY (magazine_id) REFERENCES public.magazines(id);


--
-- TOC entry 3389 (class 2606 OID 17047)
-- Name: auto_sales auto_sales_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auto_sales
    ADD CONSTRAINT auto_sales_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- TOC entry 3364 (class 2606 OID 16463)
-- Name: clients clients_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- TOC entry 3373 (class 2606 OID 16549)
-- Name: loan_payments loan_payments_loan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loan_payments
    ADD CONSTRAINT loan_payments_loan_id_fkey FOREIGN KEY (loan_id) REFERENCES public.loans(id);


--
-- TOC entry 3369 (class 2606 OID 16524)
-- Name: loans loans_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 3370 (class 2606 OID 16534)
-- Name: loans loans_magazine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_magazine_id_fkey FOREIGN KEY (magazine_id) REFERENCES public.magazines(id);


--
-- TOC entry 3371 (class 2606 OID 16519)
-- Name: loans loans_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- TOC entry 3372 (class 2606 OID 16529)
-- Name: loans loans_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- TOC entry 3361 (class 2606 OID 16605)
-- Name: magazines magazines_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.magazines
    ADD CONSTRAINT magazines_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- TOC entry 3382 (class 2606 OID 16724)
-- Name: notification_preferences notification_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification_preferences
    ADD CONSTRAINT notification_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3383 (class 2606 OID 16750)
-- Name: notifications notifications_push_token_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_push_token_id_fkey FOREIGN KEY (push_token_id) REFERENCES public.push_tokens(id);


--
-- TOC entry 3384 (class 2606 OID 16740)
-- Name: notifications notifications_recipient_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_recipient_user_id_fkey FOREIGN KEY (recipient_user_id) REFERENCES public.users(id);


--
-- TOC entry 3385 (class 2606 OID 16745)
-- Name: notifications notifications_sender_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_sender_user_id_fkey FOREIGN KEY (sender_user_id) REFERENCES public.users(id);


--
-- TOC entry 3365 (class 2606 OID 16480)
-- Name: products products_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- TOC entry 3381 (class 2606 OID 16709)
-- Name: push_tokens push_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_tokens
    ADD CONSTRAINT push_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3366 (class 2606 OID 16504)
-- Name: sales sales_magazine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_magazine_id_fkey FOREIGN KEY (magazine_id) REFERENCES public.magazines(id);


--
-- TOC entry 3367 (class 2606 OID 16494)
-- Name: sales sales_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- TOC entry 3368 (class 2606 OID 16499)
-- Name: sales sales_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- TOC entry 3374 (class 2606 OID 16584)
-- Name: transactions transactions_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 3375 (class 2606 OID 16569)
-- Name: transactions transactions_loan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_loan_id_fkey FOREIGN KEY (loan_id) REFERENCES public.loans(id);


--
-- TOC entry 3376 (class 2606 OID 16574)
-- Name: transactions transactions_loan_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_loan_payment_id_fkey FOREIGN KEY (loan_payment_id) REFERENCES public.loan_payments(id);


--
-- TOC entry 3377 (class 2606 OID 16594)
-- Name: transactions transactions_magazine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_magazine_id_fkey FOREIGN KEY (magazine_id) REFERENCES public.magazines(id);


--
-- TOC entry 3378 (class 2606 OID 16579)
-- Name: transactions transactions_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- TOC entry 3379 (class 2606 OID 16564)
-- Name: transactions transactions_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(id);


--
-- TOC entry 3380 (class 2606 OID 16589)
-- Name: transactions transactions_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- TOC entry 3362 (class 2606 OID 16600)
-- Name: users users_magazine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_magazine_id_fkey FOREIGN KEY (magazine_id) REFERENCES public.magazines(id);


--
-- TOC entry 3363 (class 2606 OID 16610)
-- Name: users users_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


-- Completed on 2025-09-09 16:20:36 +05

--
-- PostgreSQL database dump complete
--

\unrestrict 67zMrtMaPVOodK8KJTcPeXUXxnzn15x2x1IsNe0IoXM3OOicEPGVbY4v08ejncC

