import express from "express";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import { pool } from "../db";
import { authenticateToken } from "../middleware/auth";

const router = express.Router();

router.post("/register", async (req, res) => {
    try {
        const { email, username, password } = req.body;
        // backend/src/middleware/auth.ts
        import { Request, Response, NextFunction } from "express";
        import jwt from "jsonwebtoken";

        interface JwtPayload {
            id: number;
        }

        export const authenticateToken = (
            req: Request,
            res: Response,
            next: NextFunction
        ) => {
            const authHeader = req.headers["authorization"];
            const token = authHeader && authHeader.split(" ")[1];

            if (!token) {
                return res.sendStatus(401); // Unauthorized
            }

            jwt.verify(
                token,
                process.env.JWT_SECRET as string,
                (err, decoded) => {
                    if (err) {
                        return res.sendStatus(403); // Forbidden
                    }

                    const payload = decoded as JwtPayload;
                    if (!payload || !payload.id) {
                        return res.sendStatus(403); // Forbidden
                    }

                    req.user = { id: payload.id };
                    next();
                }
            );
        };
        // Валидация входных данных
        if (!email || !username || !password) {
            return res.status(400).json({
                message: "Все поля обязательны для заполнения",
            });
        }

        // Проверка существующего пользователя по email
        const emailExists = await pool.query(
            "SELECT * FROM users WHERE email = $1",
            [email]
        );

        if (emailExists.rows.length > 0) {
            return res.status(400).json({
                message: "Пользователь с таким email уже существует",
            });
        }

        // Проверка существующего пользователя по username
        const usernameExists = await pool.query(
            "SELECT * FROM users WHERE username = $1",
            [username]
        );

        if (usernameExists.rows.length > 0) {
            return res.status(400).json({
                message: "Пользователь с таким именем уже существует",
            });
        }

        // Хеширование пароля
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Создание пользователя
        const result = await pool.query(
            "INSERT INTO users (email, username, password, role) VALUES ($1, $2, $3, $4) RETURNING id, email, username, role",
            [email, username, hashedPassword, "USER"]
        );

        const user = result.rows[0];
        const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET!, {
            expiresIn: "1d",
        });

        res.json({
            token,
            user: {
                id: user.id,
                email: user.email,
                username: user.username,
                role: user.role,
            },
        });
    } catch (error) {
        console.error("Ошибка при регистрации:", error);
        res.status(500).json({ message: "Ошибка сервера при регистрации" });
    }
});

router.post("/login", async (req, res) => {
    try {
        const { email, password } = req.body;

        const result = await pool.query(
            "SELECT * FROM users WHERE email = $1",
            [email]
        );

        if (result.rows.length === 0) {
            return res.status(401).json({ message: "Invalid credentials" });
        }

        const user = result.rows[0];
        const validPassword = await bcrypt.compare(password, user.password);

        if (!validPassword) {
            return res.status(401).json({ message: "Invalid credentials" });
        }

        const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET!, {
            expiresIn: "1d",
        });

        const { password: _, ...userWithoutPassword } = user;
        res.json({
            access_token: token, // Изменено на access_token
            token_type: "Bearer", // Добавлено поле token_type
            user: userWithoutPassword, // Добавлено поле user
        });
    } catch (error) {
        res.status(500).json({ message: "Server error" });
    }
});

router.get("/me", authenticateToken, async (req, res) => {
    try {
        if (!req.user || !req.user.id) {
            return res.status(400).json({ message: "Invalid user ID" });
        }

        const result = await pool.query(
            "SELECT id, email, username, role FROM users WHERE id = $1",
            [req.user.id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ message: "User not found" });
        }

        res.json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ message: "Server error" });
    }
});

export default router;
