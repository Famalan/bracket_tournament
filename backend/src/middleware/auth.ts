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

    jwt.verify(token, process.env.JWT_SECRET as string, (err, decoded) => {
        if (err) {
            return res.sendStatus(403); // Forbidden
        }

        const payload = decoded as JwtPayload;
        if (!payload || !payload.id) {
            return res.sendStatus(403); // Forbidden
        }

        req.user = { id: payload.id };
        next();
    });
};
