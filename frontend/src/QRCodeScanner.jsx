import React, { useState, useRef, useEffect } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import { X, Camera, CheckCircle, AlertCircle } from 'lucide-react';

function QRCodeScanner({ setStartNode, onClose }) {
    const [isScanning, setIsScanning] = useState(false);
    const [error, setError] = useState(null);
    const [scannedValue, setScannedValue] = useState(null);
    const qrRef = useRef(null);
    const scannerRef = useRef(null);

    const stopScanning = async () => {
        if (scannerRef.current) {
            try {
                await scannerRef.current.stop();
                scannerRef.current.clear();
                scannerRef.current = null;
            } catch (err) {
                console.error("Error stopping scanner:", err);
            }
        }
        setIsScanning(false);
    };

    const startQR = async () => {
        if (!qrRef.current) return;

        setError(null);
        setScannedValue(null);

        try {
            scannerRef.current = new Html5Qrcode(qrRef.current.id);

            await scannerRef.current.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: { width: 250, height: 250 } },
                (decodedText) => {
                    const trimmedText = decodedText.trim();
                    setScannedValue(trimmedText);
                    setStartNode(trimmedText);

                    // Stop scanning and close after a short delay to show success
                    setTimeout(() => {
                        stopScanning();
                        if (onClose) onClose();
                    }, 5000);
                },
                (err) => {
                    // Ignore continuous scan errors (normal when no QR detected)
                }
            );

            setIsScanning(true);
        } catch (err) {
            console.error("Camera access error:", err);
            setError(err.message || "Failed to access camera. Please grant camera permissions.");
            setIsScanning(false);
        }
    };

    const handleClose = () => {
        stopScanning();
        if (onClose) onClose();
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopScanning();
        };
    }, []);

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[2000] p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-600 to-blue-700">
                    <div className="flex items-center gap-2">
                        <Camera className="w-5 h-5 text-white" />
                        <h3 className="font-bold text-white">Scan QR Code</h3>
                    </div>
                    <button
                        onClick={handleClose}
                        className="text-white hover:bg-white/20 rounded-lg p-1 transition-all"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-4">
                    {/* Scanner Container */}
                    <div
                        id="qr-reader"
                        ref={qrRef}
                        className={`w-full rounded-lg overflow-hidden ${isScanning ? 'h-80' : 'h-0'
                            }`}
                    />

                    {/* Success Message */}
                    {scannedValue && (
                        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-xl flex items-start gap-3 animate-in fade-in slide-in-from-bottom-2">
                            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                            <div>
                                <p className="font-semibold text-green-800">QR Code Scanned!</p>
                                <p className="text-sm text-green-700 mt-1">Start Point: <span className="font-mono font-bold">{scannedValue}</span></p>
                            </div>
                        </div>
                    )}

                    {/* Error Message */}
                    {error && (
                        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                            <div>
                                <p className="font-semibold text-red-800">Camera Error</p>
                                <p className="text-sm text-red-700 mt-1">{error}</p>
                            </div>
                        </div>
                    )}

                    {/* Instructions */}
                    {!isScanning && !scannedValue && !error && (
                        <div className="mb-4 p-4 bg-blue-50 border border-blue-100 rounded-xl">
                            <p className="text-sm text-blue-800">
                                Position the QR code within the camera frame. The location will be automatically detected and set as your start point.
                            </p>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-2">
                        {!isScanning ? (
                            <button
                                onClick={startQR}
                                disabled={scannedValue !== null}
                                className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg hover:shadow-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-95 flex items-center justify-center gap-2"
                            >
                                <Camera className="w-5 h-5" />
                                Start Camera
                            </button>
                        ) : (
                            <button
                                onClick={stopScanning}
                                className="flex-1 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl shadow-lg transition-all transform active:scale-95"
                            >
                                Stop Scanning
                            </button>
                        )}
                        <button
                            onClick={handleClose}
                            className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-xl transition-all"
                        >
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default QRCodeScanner;
