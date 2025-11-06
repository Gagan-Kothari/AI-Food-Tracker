"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { CameraIcon, XMarkIcon } from "@heroicons/react/24/outline"
import Quagga from "@ericblade/quagga2"

interface BarcodeScannerProps {
  onBarcodeDetected: (barcode: string) => void
  onClose: () => void
}

export default function BarcodeScanner({ onBarcodeDetected, onClose }: BarcodeScannerProps) {
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState("")
  const [showScanner, setShowScanner] = useState(false) // Track if scanner UI is shown
  const scannerRef = useRef<HTMLDivElement>(null)

  // Keep a stable onDetected callback
  const onDetected = useCallback(
    (result: any) => {
      const code = result?.codeResult?.code
      if (code) {
        stopCamera()
        onBarcodeDetected(code)
      }
    },
    [onBarcodeDetected]
  )

  const startCamera = useCallback(() => {
    setError("")
    setShowScanner(true) // Show scanner UI first
    
    // Use setTimeout to ensure DOM is rendered
    setTimeout(() => {
      if (!scannerRef.current) {
        setError("Scanner view not ready yet.")
        setShowScanner(false)
        return
      }

      setIsScanning(true)

      Quagga.init(
        {
          inputStream: {
            type: "LiveStream",
            target: scannerRef.current,
            constraints: {
              width: 640,
              height: 480,
              facingMode: { ideal: "environment" }
            }
          },
          decoder: {
            readers: [
              "code_128_reader",
              "ean_reader",
              "ean_8_reader",
              "code_39_reader",
              "code_39_vin_reader",
              "codabar_reader",
              "upc_reader",
              "upc_e_reader",
              "i2of5_reader"
            ]
          },
          locate: true,
          locator: {
            patchSize: "medium",
            halfSample: true
          }
        },
        (err) => {
          if (err) {
            console.error("QuaggaJS init error:", err)
            setError("Failed to initialize camera. Please check camera permissions and try again.")
            setIsScanning(false)
            setShowScanner(false)
            return
          }
          Quagga.start()
          Quagga.onDetected(onDetected)
        }
      )
    }, 100) // Small delay to ensure DOM is ready
  }, [onDetected])

  const stopCamera = useCallback(() => {
    if (!isScanning) return
    try {
      Quagga.stop()
      Quagga.offDetected(onDetected)
    } catch (err) {
      console.error("Error stopping Quagga:", err)
    }
    setIsScanning(false)
    setShowScanner(false)
  }, [isScanning, onDetected])

  useEffect(() => {
    return () => {
      if (isScanning) {
        stopCamera()
      }
    }
  }, [isScanning, stopCamera])

  const handleClose = useCallback(() => {
    stopCamera()
    onClose()
  }, [stopCamera, onClose])

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">Scan Barcode</h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="p-4">
          {!showScanner ? (
            <div className="text-center py-8">
              <CameraIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Scan</h3>
              <p className="text-gray-600 mb-6">
                Position the barcode within the camera view and click start scanning
              </p>
              <button
                onClick={startCamera}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Start Camera
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Loading state while camera initializes */}
              {!isScanning && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Initializing camera...</p>
                </div>
              )}
              
              {/* Quagga will inject <video> here */}
              <div
                ref={scannerRef}
                className={`relative bg-black rounded-lg overflow-hidden w-full h-64 ${
                  !isScanning ? 'hidden' : ''
                }`}
              >
                <div className="absolute inset-0 border-2 border-blue-500 border-dashed m-4 rounded-lg pointer-events-none">
                  <div className="absolute top-2 left-2 text-white text-sm bg-blue-500 px-2 py-1 rounded">
                    Position barcode here
                  </div>
                </div>
              </div>

              {isScanning && (
                <div className="text-center">
                  <button
                    onClick={stopCamera}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                  >
                    Stop Scanning
                  </button>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-100 text-red-800 rounded-lg">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}