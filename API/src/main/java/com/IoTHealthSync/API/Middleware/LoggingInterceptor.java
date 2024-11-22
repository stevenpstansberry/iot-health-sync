package com.IoTHealthSync.API.Middleware;

import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.logging.Logger;

@Component
public class LoggingInterceptor implements HandlerInterceptor {

    private static final Logger logger = Logger.getLogger(LoggingInterceptor.class.getName());

    // Method executed before the request reaches the controller
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        String requestURI = request.getRequestURI();
        String clientIP = request.getRemoteAddr();

        logger.info("Received request to " + requestURI + " from IP: " + clientIP);
        logger.info("Processing request...");

        // Returning true allows the request to continue to the controller
        return true;
    }

    // Method executed after the controller has processed the request but before the response is sent
    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, org.springframework.web.servlet.ModelAndView modelAndView) throws Exception {
        logger.info("Successfully processed request for " + request.getRequestURI());
    }

    // Method executed after the response has been sent to the client
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
        if (ex != null) {
            logger.severe("An error occurred while processing request: " + ex.getMessage());
        } else {
            logger.info("Request completed successfully.");
        }
    }
}